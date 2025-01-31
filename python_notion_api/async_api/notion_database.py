from typing import TYPE_CHECKING, Any, AsyncGenerator, Dict, List, Optional

from pydantic.v1 import BaseModel

from python_notion_api.async_api.notion_page import NotionPage
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

if TYPE_CHECKING:
    from python_notion_api.async_api.api import AsyncNotionAPI


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

    def __init__(self, api: "AsyncNotionAPI", database_id: str):
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
        """Gets the database id."""
        return self._database_id.replace("-", "")

    async def reload(self):
        """Reloads the database from Notion."""
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
    ) -> AsyncGenerator[NotionPage, None]:
        """Queries the database.

        Retrieves all pages belonging to the database that satisfy the given filters
        in the order specified by the sorts.

        Args:
            filters: Filters to apply to the query.
            sorts: Sorts to apply to the query.
            cast_cls: A subclass of a NotionPage. Allows custom
            property retrieval.

        Returns:
            Generator of NotionPage objects.
        """
        data: dict[str, Any] = {}

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
        """Gets title of the database."""
        assert self._title is not None
        return self._title

    @property
    @ensure_loaded
    def properties(self) -> Dict[str, NotionPropertyConfiguration]:
        """Gets all property configurations of the database."""
        assert self._properties is not None
        return self._properties

    @property
    @ensure_loaded
    def relations(self) -> Dict[str, RelationPropertyConfiguration]:
        """Gets all property configurations of the database that are
        relations.
        """
        assert self._properties is not None
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

        Args:
            properties: Dictionary of property names and values. Value types
            will depend on the property type. Can be the raw value
            (e.g. string, float) or an object (e.g. SelectValue,
            NumberPropertyItem)
            cover: URL of an image for the page cover.

        Returns:
            A new page.
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
