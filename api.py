import requests
import logging
import json

from notion_integration.api.models.objects import DatabaseObject
from notion_integration.api.models.properties import (
    NotionProperty, RelationProperty
)
from notion_integration.api.models.configurations import (
    RelationPropertyConfiguration,
    NotionPropertyConfiguration
)

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class NotionPage:
    def __init__(self, api, page_id):
        self.api = api
        self.page_id = page_id
        self._properties = None

    def update(self, properties):
        self.api.patch(
            endpoint=f'pages/{self.page_id}',
            data=json.dumps({
                'properties': properties
            })
        )
        self.reload()

    def reload(self):
        obj = self.api.get(endpoint=f'pages/{self.page_id}')
        self._properties = {
            key: NotionProperty.from_obj(val)
            for key, val in obj['properties'].items()
        }

    @property
    def properties(self):
        if self._properties is None:
            self.reload()
        return self._properties

    def to_dict(self, include_rels=True):
        if include_rels is True:
            return {
                key: val.value for key, val in self.properties.items()
            }
        else:
            return {
                key: val.value for key, val in self.properties.items()
                if not isinstance(val, RelationProperty)
            }

    @property
    def relations(self):
        return {
            key: val for key, val in self.properties.items()
            if isinstance(val, RelationProperty)
        }


class NotionDatabase:
    def __init__(self, api, database_id):
        self.api = api
        self.database_id = database_id
        ret = self.api.get(endpoint=f'databases/{self.database_id}')

        if ret is None:
            raise Exception(f"Error accessing database {self.database_id}")

        self.object = DatabaseObject(
            **ret
        )

        self._properties = {
            key: NotionPropertyConfiguration.from_obj(val)
            for key, val in self.object.properties.items()
        }
        self.title = "".join(
            rt.plain_text for rt in self.object.title
        )

    def query(self, filter_params={}, sort_params=[]):
        has_more = True
        cursor = None

        while has_more:
            data = {
                'start_cursor': cursor,
                'page_size': 100
                # 'filter': filter_params,
                # 'sorts': sort_params
            }

            if cursor is None:
                data.pop('start_cursor')
            response = self.api.post(
                endpoint=f'databases/{self.database_id}/query',
                data=json.dumps(data)
            )

            for page in response['results']:
                yield NotionPage(self.api, page['id'])

            has_more = response['has_more']
            cursor = response['next_cursor']

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
                headers={}, url=None, attempt=0):
        url = url or self.base_url + endpoint
        request = getattr(requests, request_type)

        headers.update(
            {
                'Authorization': f'Bearer {self.access_token}',
                'Notion-Version': '2021-05-13'
            }
        )

        response = request(
            url,
            params=params,
            data=data,
            headers=headers
        )

        if response.status_code == 200:
            return response.json()
        else:
            log.error(f"Request to {url} failed:\n{response.status_code}\n{response.text}")

    def post(self, endpoint, data=None, params={}):
        return self.request(
            request_type='post',
            endpoint=endpoint,
            data=data,
            params=params,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )

    def get(self, endpoint, params={}):
        return self.request(
            request_type='get',
            endpoint=endpoint,
            params=params,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )

    def patch(self, endpoint, params={}, data={}):
        return self.request(
            request_type='patch',
            endpoint=endpoint,
            params=params,
            data=data,
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
    db = api.get_database('94b47deaf77c4a1dbe9ba0dbb5a92791')
    pages = db.query()
    pages[0].update(
        {
            'Foo': {
                'relation': [{'id':'b85fc2c8-a426-45cb-93e5-1b29a9184121'}]
            }
        }
    )
