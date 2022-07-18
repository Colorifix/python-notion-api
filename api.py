import requests
import logging
import json

from pprint import pprint

from typing import Union, Any

from notion_integration.api.models.objects import (
    Database,
    Pagination
)

from notion_integration.api.models.properties import (
     PropertyItem,
     NotionObject,
     PropertyItemPagination,
     RichTextPagination,
     TitlePagination
)

from notion_integration.api.models.configurations import (
    RelationPropertyConfiguration,
    NotionPropertyConfiguration
)

from notion_integration.api.models.iterators import (
    PropertyItemIterator,
    RelationPropertyItemIterator
)

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class NotionPage:
    def __init__(self, api, page_id):
        self.api = api
        self.page_id = page_id
        self._properties_cache = None
        self._object = None

        self._object = self.api.get(endpoint=f'pages/{self.page_id}')
        if self._object is None:
            raise ValueError(f"Page {page_id} could not be found")

    def get(self, prop_name: str) -> Union[PropertyItemIterator, PropertyItem]:
        if prop_name in self._object.properties:
            prop_id = self._object.properties[prop_name].property_id
            ret = self.api.get(
                endpoint=f'pages/{self.page_id}/properties/{prop_id}'
            )
            if isinstance(ret, Pagination):
                generator = self.api.get_iterate(
                    endpoint=f'pages/{self.page_id}/properties/{prop_id}'
                )

                parent_id = self.parent.database_id
                parent_db = self.api.get_database(parent_id)

                prop_type = parent_db.properties[prop_name].config_type

                iterator = PropertyItemIterator.from_generator(
                    generator,
                    prop_type
                )

                return iterator

            elif isinstance(ret, PropertyItem):
                return ret
            else:
                raise TypeError("Returned property is of an unknown type")

    def set(self, prop_name: str, value: Any):
        if prop_name in self._object.properties:
            prop_id = self._object.properties[prop_name].property_id
            ret = self.api.get(
                endpoint=f'pages/{self.page_id}/properties/{prop_id}'
            )
            if hasattr(ret, "set_value"):
                ret.set_value(value)
                data = {
                    'properties': {
                        prop_name: ret.dict(
                            exclude={
                                'notion_object',
                                'next_url',
                                'propety_type',
                                'property_id'
                            }
                        )
                    }
                }
                self.api.patch(
                    endpoint=f'pages/{self.page_id}',
                    data=json.dumps(data)
                )
            else:
                raise ValueError(
                    "API does not support setting {ret.__class__}"
                    " properties at the moment."
                )

    @property
    def properties(self):
        props = {}
        for prop_name in self._object.properties:
            props[prop_name] = self.get(prop_name)

        return props

    def to_dict(self, include_rels: bool = True, rels_only=False):
        vals = {}
        for prop_name in self._object.properties:
            prop = self.get(prop_name)

            if isinstance(prop, PropertyItemIterator):
                if (not include_rels) and isinstance(
                        prop, RelationPropertyItemIterator):
                    continue
                vals[prop_name] = prop.all()
            else:
                if not rels_only:
                    vals[prop_name] = prop.value
        return vals

    def __getattr__(self, attr_key):
        return getattr(self._object, attr_key)


class NotionDatabase:
    def __init__(self, api, database_id):
        self.api = api
        self.database_id = database_id
        self.obj = self.api.get(
            endpoint=f'databases/{self.database_id}',
            cast_cls=Database
        )

        if self.obj is None:
            raise Exception(f"Error accessing database {self.database_id}")

        self._properties = {
            key: NotionPropertyConfiguration.from_obj(val)
            for key, val in self.obj.properties.items()
        }
        self.title = "".join(
            rt.plain_text for rt in self.obj.title
        )

    def query(self, filter_params={}, sort_params=[]):
        for item in self.api.post_iterate(
            endpoint=f'databases/{self.database_id}/query'
        ):
            yield NotionPage(api=self.api, page_id=item.page_id)

    @property
    def properties(self):
        return self._properties

    @property
    def relations(self):
        return {
            key: val for key, val in self._properties.items()
            if isinstance(val, RelationPropertyConfiguration)
        }


class NotionAPI:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://api.notion.com/v1/"

    def request(self, request_type, endpoint='', params={}, data=None,
                headers={}, url=None, attempt=0, cast_cls=NotionObject):
        url = url or self.base_url + endpoint
        request = getattr(requests, request_type)

        headers.update(
            {
                'Authorization': f'Bearer {self.access_token}',
                'Notion-Version': '2022-06-28'
            }
        )

        response = request(
            url,
            params=params,
            data=data,
            headers=headers
        )

        if response.status_code == 200:
            return cast_cls.from_obj(response.json())
        else:
            log.error(
                f"Request to {url} failed:"
                f"\n{response.status_code}\n{response.text}"
            )

    def post(self, endpoint, data=None, params={}, cast_cls=NotionObject):
        return self.request(
            request_type='post',
            endpoint=endpoint,
            data=data,
            params=params,
            cast_cls=cast_cls,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )

    def get(self, endpoint, params={}, cast_cls=NotionObject):
        return self.request(
            request_type='get',
            endpoint=endpoint,
            params=params,
            cast_cls=cast_cls,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
        )

    def post_iterate(self, endpoint, data={}):
        has_more = True
        cursor = None

        while has_more:
            data.update({
                'start_cursor': cursor,
                'page_size': 100
            })

            if cursor is None:
                data.pop('start_cursor')

            response = self.post(
                endpoint=endpoint,
                data=json.dumps(data)
            )

            for item in response.results:
                yield item

            has_more = response.has_more
            cursor = response.next_cursor

    def get_iterate(self, endpoint, params={}):
        has_more = True
        cursor = None

        while has_more:
            params.update({
                'start_cursor': cursor,
                'page_size': 100
            })

            if cursor is None:
                params.pop('start_cursor')

            response = self.get(
                endpoint=endpoint,
                params=params
            )

            for item in response.results:
                yield item

            has_more = response.has_more
            cursor = response.next_cursor

    def patch(self, endpoint, params={}, data={}, cast_cls=NotionObject):
        return self.request(
            request_type='patch',
            endpoint=endpoint,
            params=params,
            data=data,
            cast_cls=cast_cls,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )

    def get_database(self, database_id):
        return NotionDatabase(self, database_id)

    def get_page(self, page_id):
        return NotionPage(self, page_id)


if __name__ == '__main__':
    token = "***REMOVED***"
    api = NotionAPI(access_token=token)
    db = api.get_database('84ff07f2a274455793742db3bdb61ea8')
    page = next(db.query())
    pprint(page.to_dict(include_rels=True))
    # print(db.properties)

    # page.set('Number', 666)

