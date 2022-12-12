import json
from typing import Any, Dict, Generator, List, Literal, Optional, Type, Union
from loguru import logger

from python_notion_api.models.common import (
    FileObject,
    ParentObject
)
from python_notion_api.models.configurations import (
    NotionPropertyConfiguration, RelationPropertyConfiguration)
from python_notion_api.models.filters import FilterItem
from python_notion_api.models.iterators import (
    PropertyItemIterator, create_property_iterator, BlockIterator
)
from python_notion_api.models.objects import (
    Block, Database, NotionObjectBase, Pagination, User
)
from python_notion_api.models.objects import (
    Block, Database, NotionObjectBase, Pagination, User
)
from python_notion_api.models.properties import NotionObject, PropertyItem
from python_notion_api.models.sorts import Sort
from python_notion_api.models.values import PropertyValue, generate_value
from pydantic import BaseModel
from requests import Session
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class NotionPage:
    """Wrapper for a notion page object.

    Args:
        api: Instance of the NotionAPI.
        page_id: Id of the page.
    """

    class PatchRequest(BaseModel):
        properties: Dict[str, PropertyValue]

    # Map from property names to function names.
    # For use in subclasses
    special_properties = {}

    def __init__(self, api, page_id, database=None):
        self._api = api
        self._page_id = page_id
        self._object = None
        self.database = database

        self._object = self._api._get(endpoint=f'pages/{self._page_id}')
        self._alive = None

        if self._object is None:
            raise ValueError(f"Page {page_id} could not be found")

        if database is None:
            parent_id = self.parent.database_id
            self.database = self._api.get_database(parent_id)

    def __getattr__(self, attr_key):
        return getattr(self._object, attr_key)

    @property
    def page_id(self) -> str:
        return self._page_id.replace("-", "")

    @property
    def alive(self):
        if self._alive is None:
            self._alive = not self._object.archived
        return self._alive

    @alive.setter
    def alive(self, val: bool):
        archive_status = not val
        self._archive(archive_status)
        self._alive = val

    def add_blocks(self, blocks: List[Block]) -> BlockIterator:
        """Wrapper for add new blocks to an existing page.

        Args:
            blocks: List of Blocks to add
        """
        data = {
            "children": [
                block.dict(by_alias=True, exclude_unset=True)
                for block in blocks
            ]
        }
        new_blocks = self._api._patch(
            endpoint=f'blocks/{self.page_id}/children',
            data=json.dumps(data)
        )
        return BlockIterator(iter(new_blocks.results))

    def get_blocks(self) -> BlockIterator:
        """
        Get an iterater of all blocks in the page
        Returns:

        """

        generator = self._api._get_iterate(
            endpoint=f'blocks/{self._page_id}/children'
        )
        return BlockIterator(generator)

    def get(
        self, prop_name: str, cache: bool = True
    ) -> Union[PropertyValue, PropertyItemIterator]:
        """
        First checks if the property is 'special', if so, will call the special
        function to get that property value.
        If not, gets the property through the api.

        Args:
            prop_name: Name of the property to retrieve.
        """
        if prop_name in self.special_properties:
            # For subclasses of NotionPage
            # Any special properties should have an associated function
            # in the subclass, and a mapping from the property name
            # to the function name in self.special_properties
            # Those functions must return PropertyItemIterator or PropertyItem
            attr = getattr(self, self.special_properties[prop_name])()
            assert isinstance(attr, PropertyValue)
            return attr
        else:
            return self._direct_get(prop_name=prop_name, cache=cache)

    def _direct_get(
        self, prop_name: str, cache: bool = True
    ) -> Union[PropertyValue, PropertyItemIterator]:
        """Wrapper for 'Retrieve a page property item' action.

        Will return whatever is retrieved from the API, no special cases.

        Args:
            prop_name: Name of the property to retrieve.
            cache: Boolean to decide whether to return the info from the page
                or query the API again.
        """
        if prop_name in self._object.properties:
            prop = self._object.properties[prop_name]
            obj = PropertyItem.from_obj(prop)

            prop_id = obj.property_id
            prop_type = obj.property_type

            # We need to always query the API for formulas and rollups as
            # otherwise we might get incorrect values.
            if prop_type in ('formula', 'rollup'):
                cache = False

            if (cache and not obj.has_more):
                return PropertyValue.from_property_item(obj)

            ret = self._api._get(
                endpoint=f'pages/{self._page_id}/properties/{prop_id}',
                params={"page_size": 20}
            )

            if isinstance(ret, Pagination):
                generator = self._api._get_iterate(
                    endpoint=f'pages/{self._page_id}/properties/{prop_id}'
                )
                return create_property_iterator(generator, prop_type, prop_id)

            elif isinstance(ret, PropertyItem):
                return PropertyValue.from_property_item(ret)
        else:
            raise ValueError(f"Invalid property  name {prop_name}")

    def _archive(self, archive_status=True) -> None:
        """Wrapper for 'Archive page' action if archive_status is True,
        or 'Restore page' action if archive_status is False.
        """
        self._api._patch(
            endpoint=f'pages/{self._page_id}',
            data=json.dumps({"archived": archive_status})
        )

    def set(self, prop_name: str, value: Any) -> None:
        """Wrapper for 'Update page' action.

        Args:
            prop_name: Name of the property to update
            value: A new value of the property
        """

        if prop_name in self._object.properties:
            prop_type = self._object.properties[prop_name]["type"]

            value = generate_value(prop_type, value)
            request = NotionPage.PatchRequest(
                properties={
                    prop_name: value
                }
            )

            data = request.json(
                by_alias=True,
                exclude_unset=True
            )

            self._api._patch(
                endpoint=f'pages/{self._page_id}',
                data=data
            )
        else:
            raise ValueError(
                f"Unknown property '{prop_name}'"
            )

    @property
    def properties(self) -> Dict[
            str, PropertyValue]:
        """Returns all properties of the page.
        """
        return {
            prop_name: self.get(prop_name)
            for prop_name in self._object.properties
        }

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

            if prop.property_type == "relation":
                if include_rels:
                    vals[prop_name] = prop.value
            else:
                if not rels_only:
                    vals[prop_name] = prop.value
        return vals


class NotionBlock:
    """wrapper for notion block object

    Args:
        api: Instance of the NotionAPI.
        block_id: Id of the block.
    """
    def __init__(self, api, block_id):
        self._api = api
        self._block_id = block_id

    @property
    def block_id(self) -> str:
        return self._block_id.replace("-", "")

    def get_child_blocks(self) -> BlockIterator:
        """
        Get an iterater of all blocks in the block
        Returns:

        """
        generator = self._api._get_iterate(
            endpoint=f'blocks/{self._block_id}/children'
        )
        return BlockIterator(generator)

    def add_child_block(self, content: List[Block]) -> BlockIterator:
        """Wrapper for add new blocks to an existing page.

        Args:
            content: Content of the new block.
        """
        data = {
            "children": [
                block.dict(by_alias=True, exclude_unset=True)
                for block in content
            ]
        }
        new_blocks = self._api._patch(
            endpoint=f'blocks/{self.block_id}/children',
            data=json.dumps(data)
        )
        return BlockIterator(iter(new_blocks.results))

    def set(self, block: Block) -> Block:
        """
        Updates the content of a Block. The entire content is replaced.
        Args:
            block: Block with the new values.

        Returns:

        """
        data = block.dict(by_alias=True, exclude_unset=True)
        new_block = self._api._patch(
            endpoint=f'blocks/{self.block_id}',
            data=json.dumps(data)
        )
        return new_block


class NotionDatabase:
    """Wrapper for a Notion database object.

    Args:
        api: Instance of the NotionAPI.
        database_id: Id of the database.
    """

    class CreatePageRequest(BaseModel):
        parent: ParentObject
        properties: Dict[str, PropertyValue]
        cover: Optional[FileObject]

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
        return self._database_id.replace("-", "")

    def query(self,
              filters: Optional[FilterItem] = None,
              sorts: Optional[List[Sort]] = None,
              cast_cls=NotionPage
              ) -> Generator[NotionPage, None, None]:
        """A wrapper for 'Query a database' action.

        Retrieves all pages belonging to the database.

        Args:
            filters:
            sorts:
            cast_cls: A subclass of a NotionPage. Allows custom
            property retrieval

        """
        data = {}
        if filters is not None:
            filters = filters.dict(
                by_alias=True,
                exclude_unset=True
            )
            data['filter'] = filters

        if sorts is not None:
            data['sorts'] = [
                sort.dict(
                    by_alias=True,
                    exclude_unset=True
                )
                for sort in sorts
            ]

        for item in self._api._post_iterate(
            endpoint=f'databases/{self._database_id}/query',
            data=data
        ):
            yield cast_cls(
                api=self._api, database=self, page_id=item.page_id
            )

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
            type_ = prop_value.property_type

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

    def create_page(self, properties: Dict[str, Any] = {},
                    cover_url: Optional[str] = None,
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

        validated_properties = {}
        for prop_name, prop_value in properties.items():
            prop = self.properties.get(prop_name, None)
            if prop is None:
                raise ValueError(f"Unknown property: {prop_name}")
            value = generate_value(prop.config_type, prop_value)
            validated_properties[prop_name] = value

        request = NotionDatabase.CreatePageRequest(
            parent=ParentObject(
                type="database_id",
                database_id=self.database_id
            ),
            properties=validated_properties,
            cover=(
                FileObject.from_url(cover_url)
                if cover_url is not None else None
            )
        )

        data = request.json(
            by_alias=True,
            exclude_unset=True
        )

        new_page = self._api._post(
            "pages",
            data=data
        )

        return NotionPage(
            api=self._api,
            page_id=new_page.page_id,
            database=self
        )


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
            logger.error(
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
                'page_size': 40
            })

            if cursor is None:
                params.pop('start_cursor')

            response = self._get(
                endpoint=endpoint,
                params=params
            )

            if hasattr(response, 'property_item'):
                # Required for rollups
                property_item = response.property_item
            else:
                # property doesn't exist for Blocks
                property_item = None

            for item in response.results:
                yield item, property_item

            has_more = response.has_more
            cursor = response.next_cursor

    def get_database(self, database_id: str) -> NotionDatabase:
        """ Wrapper for 'Retrieve a database' action.

        Args:
            database_id: Id of the database to fetch.
        """
        return NotionDatabase(self, database_id)

    def get_page(self, page_id, page_cast=NotionPage) -> NotionPage:
        """ Wrapper for 'Retrieve a dpage' action.

        Args:
            page_id: Id of the database to fetch.
            page_cast: A subclass of a NotionPage. Allows custom
            property retrieval
        """
        return page_cast(self, page_id)

    def get_block(self, block_id) -> NotionBlock:
        """ Wrapper for 'Retrieve a block' action.

        Args:
            block_id: Id of the block to fetch.
        """
        return NotionBlock(self, block_id)

    def me(self) -> User:
        return self._get("users/me")
