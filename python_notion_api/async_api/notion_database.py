from typing import Any, Dict, Generator, List, Optional

from pydantic import BaseModel

from python_notion_api.async_api import NotionPage
from python_notion_api.async_api.utils import ensure_loaded
from python_notion_api.models.common import FileObject, ParentObject
from python_notion_api.models.configurations import (
    NotionPropertyConfiguration,
    RelationPropertyConfiguration,
)
from python_notion_api.models.filters import FilterItem
from python_notion_api.models.objects import Database
from python_notion_api.models.sorts import Sort
from python_notion_api.models.values import PropertyValue, generate_value


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
        self._object = None
        self._properties = None
        self._title = None

    @ensure_loaded
    def __getattr__(self, attr_key):
        return getattr(self._object, attr_key)

    @property
    def database_id(self) -> str:
        return self._database_id.replace("-", "")

    async def reload(self):
        self._object = await self._api._get(
            endpoint=f"databases/{self._database_id}", cast_cls=Database
        )

        if self._object is None:
            raise Exception(f"Error loading database {self._database_id}")

        self._properties = {
            key: NotionPropertyConfiguration.from_obj(val)
            for key, val in self._object.properties.items()
        }
        self._title = "".join(rt.plain_text for rt in self._object.title)

    async def query(
        self,
        filters: Optional[FilterItem] = None,
        sorts: Optional[List[Sort]] = None,
        page_limit: Optional[int] = None,
        cast_cls=NotionPage,
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
            filters = filters.dict(by_alias=True, exclude_unset=True)
            data["filter"] = filters

        if sorts is not None:
            data["sorts"] = [
                sort.dict(by_alias=True, exclude_unset=True) for sort in sorts
            ]

        async for item in self._api._post_iterate(
            endpoint=f"databases/{self._database_id}/query",
            data=data,
            page_limit=page_limit,
        ):
            yield cast_cls(
                api=self._api, database=self, page_id=item.page_id, obj=item
            )

    @property
    @ensure_loaded
    def title(self) -> str:
        """Returns a title of the database."""
        return self._title

    @property
    @ensure_loaded
    def properties(self) -> Dict[str, NotionPropertyConfiguration]:
        """Returns all property configurations of the database."""
        return self._properties

    @property
    @ensure_loaded
    def relations(self) -> Dict[str, RelationPropertyConfiguration]:
        """Returns all property configurations of the database that are
        relations.
        """
        return {
            key: val
            for key, val in self._properties.items()
            if isinstance(val, RelationPropertyConfiguration)
        }

    async def create_page(
        self,
        properties: Dict[str, Any] = {},
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
                type="database_id", database_id=self.database_id
            ),
            properties=validated_properties,
            cover=(
                FileObject.from_url(cover_url)
                if cover_url is not None
                else None
            ),
        )

        data = request.json(by_alias=True, exclude_unset=True)

        new_page = await self._api._post("pages", data=data)

        return NotionPage(
            api=self._api,
            page_id=new_page.page_id,
            obj=new_page,
            database=self,
        )
