from typing import Union, Any, Literal, Dict, Optional, Type, Generator, List

import logging
import json

from requests import Session
from requests.adapters import HTTPAdapter

from requests.packages.urllib3.util.retry import Retry

from notion_integration.api.models.objects import (
    Database,
    Pagination,
    NotionObjectBase
)

from notion_integration.api.models.properties import (
     PropertyItem,
     NotionObject,
     RollupPagination
)

from notion_integration.api.models.configurations import (
    RelationPropertyConfiguration,
    NotionPropertyConfiguration
)

from notion_integration.api.models.iterators import (
    PropertyItemIterator,
    RelationPropertyItemIterator,
    RollupPropertyItemIterator
)

log = logging.getLogger(__name__)


class NotionPage:
    """Wrapper for a notion page object.

    Args:
        api: Instance of the NotionAPI.
        page_id: Id of the page.
    """
    def __init__(self, api, page_id):
        self._api = api
        self._page_id = page_id
        self._properties_cache = None
        self._object = None

        self._object = self._api._get(endpoint=f'pages/{self._page_id}')
        if self._object is None:
            raise ValueError(f"Page {page_id} could not be found")

    def __getattr__(self, attr_key):
        return getattr(self._object, attr_key)

    @property
    def page_id(self) -> str:
        return self._page_id

    def get(self, prop_name: str) -> Union[PropertyItemIterator, PropertyItem]:
        """Wrapper for 'Retrieve a page property item' action.

        Args:
            prop_name: Name of the property to retrieve.
        """
        if prop_name in self._object.properties:
            prop_id = self._object.properties[prop_name].property_id
            ret = self._api._get(
                endpoint=f'pages/{self._page_id}/properties/{prop_id}'
            )
            if isinstance(ret, RollupPagination):
                # There are a few types of Rollup properties.
                # Those of an array type store a list of items in the
                # results attribute
                # Need to treat this as a special case
                return RollupPropertyItemIterator.from_pagination(ret)
            elif isinstance(ret, Pagination):
                generator = self._api._get_iterate(
                    endpoint=f'pages/{self._page_id}/properties/{prop_id}'
                )

                parent_id = self.parent.database_id
                parent_db = self._api.get_database(parent_id)

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

    def set(self, prop_name: str, value: Any) -> None:
        """Wrapper for 'Update page' action.

        Args:
            prop_name: Name of the property to update
            value: A new value of the property
        """
        if prop_name in self._object.properties:
            prop_id = self._object.properties[prop_name].property_id
            ret = self._api._get(
                endpoint=f'pages/{self._page_id}/properties/{prop_id}'
            )
            if hasattr(ret, "set_value"):
                ret.set_value(value)
                data = {
                    'properties': {
                        prop_name: ret.get_dict_for_post()
                    }
                }
                self._api._patch(
                    endpoint=f'pages/{self._page_id}',
                    data=json.dumps(data)
                )
            else:
                raise ValueError(
                    f"API does not support setting {ret.__class__}"
                    " properties at the moment."
                )

    @property
    def properties(self) -> Dict[
            str, Union[PropertyItemIterator, PropertyItem]]:
        """Returns all properties of the page.
        """
        props = {}
        for prop_name in self._object.properties:
            props[prop_name] = self.get(prop_name)

        return props

    def to_dict(self,
                include_rels: bool = True,
                rels_only=False,
                properties: Optional[Union[str, List]] = None) \
            -> Dict[str, Union[str, List]]:
        """Returns all properties of the page as simple values.

        Args:
            include_rels: Include relations.
            rels_only: Return relations only.
            properties: List of properties to return. If None, will
            get values for all properties.
        """
        if properties is None:
            properties = self._object.properties
        vals = {}
        for prop_name in properties:
            prop = self.get(prop_name)

            if isinstance(prop, RelationPropertyItemIterator):
                if include_rels:
                    vals[prop_name] = prop.all()
            elif isinstance(prop, PropertyItemIterator):
                if not rels_only:
                    vals[prop_name] = prop.all()
            else:
                if not rels_only:
                    vals[prop_name] = prop.value
        return vals


class NotionDatabase:
    """Wrapper for a Notion database object.

    Args:
        api: Instance of the NotionAPI.
        database_id: Id of the database.
    """
    def __init__(self, api, database_id):
        self._api = api
        self._database_id = database_id
        self._object = self._api._get(
            endpoint=f'databases/{self._database_id}',
            cast_cls=Database
        )

        if self._object is None:
            raise Exception(f"Error accessing database {self._database_id}")

        self._properties = {
            key: NotionPropertyConfiguration.from_obj(val)
            for key, val in self._object.properties.items()
        }
        self._title = "".join(
            rt.plain_text for rt in self._object.title
        )

    @property
    def database_id(self) -> str:
        return self._database_id

    def query(self, sort_filter: Optional[Dict[str, Dict]] = {}) -> \
            Generator[NotionPage, None, None]:
        """A wrapper for 'Query a database' action.

        Retrieves all pages belonging to the database.

        Args:
            sort_filter: dictionary with any filtering and sorting parameters.
            Should match the formats described here:
            https://developers.notion.com/reference/post-database-query
            https://developers.notion.com/reference/post-database-query-filter
            https://developers.notion.com/reference/post-database-query-sort

        """
        for item in self._api._post_iterate(
            endpoint=f'databases/{self._database_id}/query',
            data=sort_filter
        ):
            yield NotionPage(api=self._api, page_id=item.page_id)

    @property
    def title(self) -> str:
        """Returns a title of the database.
        """
        return self._title

    @property
    def properties(self) -> Dict[str, NotionPropertyConfiguration]:
        """Returns all property configurations of the database.
        """
        return self._properties

    @property
    def relations(self) -> Dict[str, RelationPropertyConfiguration]:
        """Returns all property configurations of the database that are
        relations.
        """
        return {
            key: val for key, val in self._properties.items()
            if isinstance(val, RelationPropertyConfiguration)
        }

    def get_property(self, prop_config: Any, prop_value: str) -> Any:
        """Create property for a given property configuration.
        """

        if isinstance(prop_value, (PropertyItem, PropertyItemIterator)):
            if isinstance(prop_value, PropertyItem):
                type_ = prop_value.property_type
            else:
                type_ = prop_value.iterator_type

            if type_ != prop_config.config_type:
                # Have a mismatch between the property type and the
                # given item
                raise TypeError(f'Item {prop_value.__class__} given as '
                                f'the value for property '
                                f'{prop_config.__class__}')
            new_prop = prop_value

        else:
            new_prop = prop_config.create_property(prop_value)

        return new_prop

    def create_filter(self, properties):
        """Create a filter objects in json format. Multiple properties are
        joined in an AND filter. OR filters are not yet supported.
        """

        property_configs = self.properties

        filters = []

        for prop_name, (prop_query, prop_value) in properties.items():

            property_config = property_configs[prop_name]
            filter_dict = {
                property_config.config_type: {prop_query: prop_value}
            }

            prop_dict = {"property": prop_name}
            filter_dict = [prop_dict | filter_dict]
            filters += filter_dict

        # Single filter
        if len(filters) == 1:
            return {"filter": filters[0]}

        # Compound AND filter
        else:
            return{
                "filter": {
                    "and": filters
                }
            }

    def create_page(self, properties: Dict[str, Any],
                    cover: Optional[str] = None,
                    ) -> NotionPage:
        """Creates a new page in the Database and updates the new page with
        the properties.
        Status, Files or any of the advanced properties are not yet supported.

        Args:
            properties: Dictionary of property names and values. Value types
            will depend on the property type. Can be the raw value
            (e.g. string, float) or an object (e.g. SelectValue,
            NumberPropertyItem)
            cover: URL of an image for the page cover. E.g. a gdrive url.
        """

        # Create an empty page in the database
        data = {
            "parent": {
                "database_id": self.database_id
            },
            'properties': {}
        }
        property_configs = self.properties

        for prop_name, prop_value in properties.items():

            # For each property name get the property configuration
            property_config = property_configs[prop_name]
            new_prop = self.get_property(property_config, prop_value)
            data['properties'][prop_name] = new_prop.get_dict_for_post()

        if cover is not None:
            data['cover'] = {
                "type": "external",
                "external": {
                    "url": cover
                }
            }

        new_page = self._api._post("pages", data=json.dumps(data))

        return new_page


class NotionAPI:
    """Main class for Notion API wrapper.

    Args:
        access_token: Notion access token
        api_version: Version of the notion API
    """
    def __init__(self, access_token: str, api_version='2022-06-28'):
        self._access_token = access_token
        self._base_url = "https://api.notion.com/v1/"
        self._api_version = api_version

        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._http = Session()

        self._http.mount("https://", adapter)

    def _request(
            self, request_type: Literal['get', 'post', 'patch'],
            endpoint: str = '',
            params: Dict[str, Any] = {},
            data: Optional[str] = None,
            cast_cls: Type[NotionObjectBase] = NotionObject
            ) -> Optional[NotionObject]:
        """Main request handler.

        Should not be called directly, for internal use only.

        Args:
            request_type: Type of the http request to make.
            endpoint: Endpoint of the request. Will be prepened with the
                notion API base url.
            params: Params to pass to the request.
            data: Data to pass to the request.
            cast_cls: A NotionObjectBase class to auto-cast the response of the
                request to.
        """
        url = self._base_url + endpoint
        request = getattr(self._http, request_type)

        headers = {
            'Authorization': f'Bearer {self._access_token}',
            'Notion-Version': f'{self._api_version}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

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

    def _post(self,
              endpoint: str,
              data: Optional[str] = None,
              cast_cls: Type[NotionObjectBase] = NotionObject
              ) -> Optional[NotionObject]:
        """Wrapper for post requests.

        Should not be called directly, for internal use only.

        Args:
            endpoint: Endpoint of the request. Will be prepened with the
                notion API base url.
            data: Data to pass to the request.
            cast_cls: A NotionObjectBase class to auto-cast the response of the
                request to.
        """
        return self._request(
            request_type='post',
            endpoint=endpoint,
            data=data,
            cast_cls=cast_cls
        )

    def _get(self, endpoint: str,
             params: Dict[str, str] = {},
             cast_cls: Type[NotionObjectBase] = NotionObject
             ) -> Optional[NotionObject]:
        """Wrapper for post requests.

        Should not be called directly, for internal use only.

        Args:
            endpoint: Endpoint of the request. Will be prepened with the
                notion API base url.
            params: Params to pass to the request.
            cast_cls: A NotionObjectBase class to auto-cast the response of the
                request to.
        """
        return self._request(
            request_type='get',
            endpoint=endpoint,
            params=params,
            cast_cls=cast_cls,
        )

    def _patch(self, endpoint: str,
               params: Dict[str, str] = {},
               data: Optional[str] = None,
               cast_cls=NotionObject) -> NotionObject:
        """Wrapper for patch requests.

        Should not be called directly, for internal use only.

        Args:
            endpoint: Endpoint of the request. Will be prepened with the
                notion API base url.
            params: Params to pass to the request.
            data: Data to pass to the request.
            cast_cls: A NotionObjectBase class to auto-cast the response of the
                request to.
        """
        return self._request(
            request_type='patch',
            endpoint=endpoint,
            params=params,
            data=data,
            cast_cls=cast_cls
        )

    def _post_iterate(self, endpoint: str,
                      data: Dict[str, str] = {}
                      ) -> Generator[PropertyItem, None, None]:
        """Wrapper for post requests where expected return type is Pagination.

        Should not be called directly, for internal use only.

        Args:
            endpoint: Endpoint of the request. Will be prepened with the
                notion API base url.
            data: Data to pass to the request.
        """
        has_more = True
        cursor = None

        while has_more:
            data.update({
                'start_cursor': cursor,
                'page_size': 100
            })

            if cursor is None:
                data.pop('start_cursor')

            response = self._post(
                endpoint=endpoint,
                data=json.dumps(data)
            )

            for item in response.results:
                yield item

            has_more = response.has_more
            cursor = response.next_cursor

    def _get_iterate(self, endpoint: str,
                     params: Dict[str, str] = {}
                     ) -> Generator[PropertyItem, None, None]:
        """Wrapper for get requests where expected return type is Pagination.

        Should not be called directly, for internal use only.

        Args:
            endpoint: Endpoint of the request. Will be prepened with the
                notion API base url.
            params: Params to pass to the request.
        """
        has_more = True
        cursor = None

        while has_more:
            params.update({
                'start_cursor': cursor,
                'page_size': 100
            })

            if cursor is None:
                params.pop('start_cursor')

            response = self._get(
                endpoint=endpoint,
                params=params
            )

            for item in response.results:
                yield item

            has_more = response.has_more
            cursor = response.next_cursor

    def get_database(self, database_id: str) -> NotionDatabase:
        """ Wrapper for 'Retrieve a database' action.

        Args:
            database_id: Id of the database to fetch.
        """
        return NotionDatabase(self, database_id)

    def get_page(self, page_id) -> NotionPage:
        """ Wrapper for 'Retrieve a dpage' action.

        Args:
            page_id: Id of the database to fetch.
        """
        return NotionPage(self, page_id)
