import json
from typing import TYPE_CHECKING, Any, Optional, Union

from pydantic.v1 import BaseModel

from python_notion_api.async_api.iterators import (
    AsyncBlockIterator,
    AsyncPropertyItemIterator,
    create_property_iterator,
)
from python_notion_api.async_api.utils import ensure_loaded
from python_notion_api.models.objects import Block, Database, Page, Pagination
from python_notion_api.models.properties import PropertyItem
from python_notion_api.models.values import PropertyValue, generate_value

if TYPE_CHECKING:
    from python_notion_api.async_api.api import AsyncNotionAPI


class NotionPage:
    """Wrapper for a Notion page object.

    Args:
        api: Instance of the NotionAPI.
        page_id: Id of the page.
    """

    class PatchRequest(BaseModel):
        properties: dict[str, PropertyValue]

    class AddBlocksRequest(BaseModel):
        children: list[Block]

    # Map from property names to function names.
    # For use in subclasses
    special_properties: dict[str, str] = {}

    def __init__(
        self,
        api: "AsyncNotionAPI",
        page_id: str,
        obj: Optional[Page] = None,
        database: Optional[Database] = None,
    ):
        self._api = api
        self._page_id = page_id
        self._object = obj
        self.database = database

    async def reload(self):
        """Reloads page from Notion."""
        self._object = await self._api._get(endpoint=f"pages/{self._page_id}")
        if self._object is not None:
            parent_id = self.parent.database_id
            if parent_id is not None:
                self.database = await self._api.get_database(parent_id)

    @ensure_loaded
    def __getattr__(self, attr_key: str):
        return getattr(self._object, attr_key)

    @property
    def page_id(self) -> str:
        """Returns the page id."""
        return self._page_id.replace("-", "")

    @property
    @ensure_loaded
    def is_alive(self) -> bool:
        """Checks if the page is archived.

        Returns:
            `True` if the page is not archived, False otherwise.
        """
        assert self._object is not None
        return not self._object.archived

    async def archive(self):
        """Archives the page"""
        await self._archive(True)

    async def unarchive(self):
        """Unarchives the page"""
        await self._archive(False)

    async def _archive(self, archive_status=True) -> None:
        """Changes archive status of the page.

        Args:
            archive_status: Whether to archive or unarchive the page.
        """
        await self._api._patch(
            endpoint=f"pages/{self._page_id}",
            data=json.dumps({"archived": archive_status}),
        )

    @ensure_loaded
    async def set(
        self, prop_key: str, value: Any, reload_page: bool = False
    ) -> None:
        """Sets a single page property.

        Args:
            prop_key: Name or id of the property to update.
            value: A new value of the property.
            reload_page: Whether to reload the page after updating the property.
        """

        prop_name = self._get_prop_name(prop_key=prop_key)

        if prop_name is None:
            raise ValueError(f"Unknown property '{prop_name}'")

        assert self._object is not None

        prop_type = self._object.properties[prop_name]["type"]

        value = generate_value(prop_type, value)
        request = NotionPage.PatchRequest(properties={prop_name: value})

        data = request.json(by_alias=True, exclude_unset=True)

        await self._api._patch(endpoint=f"pages/{self._page_id}", data=data)

        if reload_page:
            await self.reload()

    @ensure_loaded
    async def update(
        self, properties: dict[str, Any], reload_page: bool = False
    ) -> None:
        """Updates the page with a dictionary of new values.

        Args:
            properties: A dictionary mapping property keys to new
                values.
            reload_page: Whether to reload the page after updating the properties.
        """
        values = {}
        for prop_key, value in properties.items():
            prop_name = self._get_prop_name(prop_key=prop_key)

            if prop_name is None:
                raise ValueError(f"Unknown property '{prop_name}'")

            assert self._object is not None

            prop_type = self._object.properties[prop_name]["type"]

            value = generate_value(prop_type, value)
            values[prop_name] = value

        request = NotionPage.PatchRequest(properties=values)

        data = request.json(by_alias=True, exclude_unset=True)

        await self._api._patch(endpoint=f"pages/{self._page_id}", data=data)

        if reload_page:
            await self.reload()

    @ensure_loaded
    async def get_properties(
        self, raw: bool = False
    ) -> dict[str, PropertyValue]:
        """Gets all properties of the page."""
        assert self._object is not None
        return {
            prop_name: await self.get(prop_name, raw=raw)
            for prop_name in self._object.properties
        }

    @ensure_loaded
    async def to_dict(
        self,
        include_rels: bool = True,
        rels_only=False,
        properties: Optional[dict] = None,
    ) -> dict[str, Union[str, list]]:
        """ "Returns all properties of the page as a dict of builtin type values.

        Args:
            include_rels: Include relations.
            rels_only: Return relations only.
            properties: List of properties to return. If `None`, will
                get values for all properties.
        """
        if properties is None:
            assert self._object is not None
            properties = self._object.properties
        vals = {}

        for prop_name in properties:
            prop = await self.get(prop_name, raw=True)

            if isinstance(prop, AsyncPropertyItemIterator):
                value = await prop.get_value()
            else:
                value = prop.value

            if prop.property_type == "relation":
                if include_rels:
                    vals[prop_name] = value
            else:
                if not rels_only:
                    vals[prop_name] = value
        return vals

    async def add_blocks(self, blocks: list[Block]) -> AsyncBlockIterator:
        """Adds new blocks to the page.

        Args:
            blocks: List of Blocks to add.

        Returns:
            Iterator of new blocks.
        """
        request = NotionPage.AddBlocksRequest(children=blocks)

        data = request.json(
            by_alias=True, exclude_unset=True, exclude_none=True
        )

        new_blocks = await self._api._patch(
            endpoint=f"blocks/{self.page_id}/children", data=data
        )
        return AsyncBlockIterator(iter(new_blocks.results))

    async def get_blocks(self) -> AsyncBlockIterator:
        """Gets all blocks in the page.

        Returns:
            Iterator of blocks is returned.
        """

        generator = self._api._get_iterate(
            endpoint=f"blocks/{self._page_id}/children"
        )
        return AsyncBlockIterator(generator)

    @ensure_loaded
    async def get(
        self,
        prop_key: str,
        cache: bool = True,
        safety_off: bool = False,
        raw: bool = False,
    ) -> Union[PropertyValue, AsyncPropertyItemIterator, None]:
        """Gets a single page property.

        First checks if the property is 'special', if so, will call the special
        function to get that property value.
        If not, gets the property through the api.

        Args:
            prop_key: Name or id of the property to retrieve.
            cache: If `True` and the property has been retrieved before, will return a cached value.
                Use `False` to force a new API call.
            safety_off: If `True` will use cached values of rollups and
                formulas.
        """
        if prop_key in self.special_properties:
            # For subclasses of NotionPage
            # Any special properties should have an associated function
            # in the subclass, and a mapping from the property name
            # to the function name in self.special_properties
            # Those functions must return PropertyItemIterator or PropertyItem
            attr = getattr(self, self.special_properties[prop_key])()
            assert isinstance(attr, PropertyValue)
            property_value = attr
        else:
            property_value = await self._direct_get(
                prop_key=prop_key, cache=cache, safety_off=safety_off
            )

        if raw:
            return property_value
        else:
            if isinstance(property_value, AsyncPropertyItemIterator):
                return await property_value.get_value()
            return property_value.value

    async def _direct_get(
        self, prop_key: str, cache: bool = True, safety_off: bool = False
    ) -> Union[PropertyValue, AsyncPropertyItemIterator, None]:
        """Wrapper for 'Retrieve a page property item' action.

        Will return whatever is retrieved from the API, no special cases.

        Args:
            prop_key: Name or id of the property to retrieve.
            cache: Boolean to decide whether to return the info from the page
                or query the API again.
            safety_off: If `True` will use cached values of rollups and
                formulas
        """
        prop_name = self._get_prop_name(prop_key)

        if prop_name is None:
            raise ValueError(f"Invalid property key '{prop_key}'")

        assert self._object is not None

        prop = self._object.properties[prop_name]

        obj = PropertyItem.from_obj(prop)

        prop_id = obj.property_id
        prop_type = obj.property_type

        # We need to always query the API for formulas and rollups as
        # otherwise we might get incorrect values.
        if not safety_off and prop_type in ("formula", "rollup"):
            cache = False

        if cache and not obj.has_more:
            return PropertyValue.from_property_item(obj)

        ret = await self._api._get(
            endpoint=f"pages/{self._page_id}/properties/{prop_id}",
            params={"page_size": 20},
        )

        if isinstance(ret, Pagination):
            generator = self._api._get_iterate(
                endpoint=f"pages/{self._page_id}/properties/{prop_id}"
            )
            return create_property_iterator(generator, obj)

        elif isinstance(ret, PropertyItem):
            return PropertyValue.from_property_item(ret)
        else:
            return None

    def _get_prop_name(self, prop_key: str) -> Optional[str]:
        """Gets propetry name from property key.

        Args:
            prop_key: Either a property name or property id.

        Returns:
            Property name or `None` if key is invalid.
        """
        assert self._object is not None
        _properties = self._object.properties
        prop_name = next(
            (
                key
                for key in _properties
                if key == prop_key or _properties[key]["id"] == prop_key
            ),
            None,
        )

        return prop_name
