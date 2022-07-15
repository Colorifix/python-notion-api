import requests
import logging
import json

from notion_integration.api.models.objects import (
    Database,
    Pagination
)

from notion_integration.api.models.properties import (
     NotionObject,
     PropertyItemPagination,
     RichTextPagination,
     TitlePagination
)
from notion_integration.api.models.configurations import (
    RelationPropertyConfiguration,
    NotionPropertyConfiguration
)

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class PropertyItemIterator:
    def __init__(self, generator):
        self.generator = generator

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.generator).value


class StringPropertyItemIterator(PropertyItemIterator):
    def all(self):
        return "".join([item.value for item in self.generator])


class ListPropertyItemIterator(PropertyItemIterator):
    def all(self):
        return [item.value for item in self.generator]


class NotionPage:
    def __init__(self, api, page_id):
        self.api = api
        self.page_id = page_id
        self._properties_cache = None
        self._object = None

        self._object = self.api.get(endpoint=f'pages/{self.page_id}')
        if self._object is None:
            raise ValueError(f"Page {page_id} could not be found")

    def _read_property(self, prop_name):
        if prop_name in self._object.properties:
            prop_id = self._object.properties[prop_name].property_id
            ret = self.api.get(
                endpoint=f'pages/{self.page_id}/properties/{prop_id}'
            )
            if isinstance(ret, Pagination):
                generator = self.api.get_iterate(
                    endpoint=f'pages/{self.page_id}/properties/{prop_id}'
                )

                if (
                    isinstance(ret, TitlePagination) or
                    isinstance(ret, RichTextPagination)
                ):
                    return StringPropertyItemIterator(generator)
                else:
                    return ListPropertyItemIterator(generator)
            else:
                return ret.value

    # @property
    # def properties(self):
    #     if self._properties is None:
    #         self.reload()
    #     return self._properties

    # def to_dict(self, include_rels=True):
    #     if include_rels is True:
    #         return {
    #             key: val.value for key, val in self.properties.items()
    #         }
    #     else:
    #         return {
    #             key: val.value for key, val in self.properties.items()
    #             if not isinstance(val, RelationProperty)
    #         }

    # def __getattr__(self, key):
    #     breakpoint()
    #     prop_key = next(
    #         (
    #             pk for pk in self._properties
    #             if slugify(pk) == key
    #         ),
    #         None
    #     )

    #     return self._properties[prop_key]

    # @property
    # def last_edited_time(self):
    #     if self.object is None:
    #         self.reload()
    #     return self.object.last_edited_time

    # @property
    # def relations(self):
    #     return {
    #         key: val for key, val in self.properties.items()
    #         if isinstance(val, RelationProperty)
    #     }


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
            yield NotionPage(api=api, page_id=item.page_id)

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


if __name__ == '__main__':
    token = "***REMOVED***"
    api = NotionAPI(access_token=token)
    db = api.get_database('af4a974eda13475d820580d84a71cf4c')
    page = next(db.query())
    breakpoint()
    print(page._read_property("Link").all())
