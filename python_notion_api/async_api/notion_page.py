import json
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

from python_notion_api.async_api.iterators import (
    AsyncBlockIterator,
    AsyncPropertyItemIterator,
    create_property_iterator,
)
from python_notion_api.async_api.utils import ensure_loaded
from python_notion_api.models.objects import Block, Pagination
from python_notion_api.models.properties import PropertyItem
from python_notion_api.models.values import PropertyValue, generate_value


class NotionPage:
    """Wrapper for a notion page object.

    Args:
        api: Instance of the NotionAPI.
        page_id: Id of the page.
    """

    class PatchRequest(BaseModel):
        properties: Dict[str, PropertyValue]

    class AddBlocksRequest(BaseModel):
        children: List[Block]

    # Map from property names to function names.
    # For use in subclasses
    special_properties = {}

    def __init__(self, api, page_id, obj=None, database=None):
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
    def __getattr__(self, attr_key):
        return getattr(self._object, attr_key)

    @property
    def page_id(self) -> str:
        return self._page_id.replace("-", "")

    @property
    @ensure_loaded
    def is_alive(self):
        return not self._object.archived

    async def archive(self):
        await self._archive(True)

    async def unarchive(self):
        await self._archive(False)

    async def _archive(self, archive_status=True) -> None:
        """Wrapper for 'Archive page' action if archive_status is True,
        or 'Restore page' action if archive_status is False.
        """
        await self._api._patch(
            endpoint=f"pages/{self._page_id}",
            data=json.dumps({"archived": archive_status}),
        )

    @ensure_loaded
    async def set(
        self, prop_key: str, value: Any, reload_page: bool = False
    ) -> None:
        """Wrapper for 'Update page' action.

        Args:
            prop_key: Name or id of the property to update
            value: A new value of the property
        """

        prop_name = self._get_prop_name(prop_key=prop_key)

        if prop_name is None:
            raise ValueError(f"Unknown property '{prop_name}'")

        prop_type = self._object.properties[prop_name]["type"]

        value = generate_value(prop_type, value)
        request = NotionPage.PatchRequest(properties={prop_name: value})

        data = request.json(by_alias=True, exclude_unset=True)

        await self._api._patch(endpoint=f"pages/{self._page_id}", data=data)

        if reload_page:
            await self.reload()

    @ensure_loaded
    async def update(
        self, properties: Dict[str, Any], reload_page: bool = False
    ) -> None:
        """Update page with a dictionary of new values.

        Args:
            properties: A dictionary mapping property keys to new
                values.
        """
        values = {}
        for prop_key, value in properties.items():
            prop_name = self._get_prop_name(prop_key=prop_key)

            if prop_name is None:
                raise ValueError(f"Unknown property '{prop_name}'")

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
    ) -> Dict[str, PropertyValue]:
        """Returns all properties of the page."""
        return {
            prop_name: await self.get(prop_name, raw=raw)
            for prop_name in self._object.properties
        }

    @ensure_loaded
    async def to_dict(
        self,
        include_rels: bool = True,
        rels_only=False,
        properties: Optional[Union[str, List]] = None,
    ) -> Dict[str, Union[str, List]]:
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

    async def add_blocks(self, blocks: List[Block]) -> AsyncBlockIterator:
        """Wrapper for add new blocks to an existing page.

        Args:
            blocks: List of Blocks to add

        Returns:
            Iterator of blocks is returned.
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
        """
        Get an iterater of all blocks in the page

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
    ) -> Union[PropertyValue, AsyncPropertyItemIterator]:
        """
        First checks if the property is 'special', if so, will call the special
        function to get that property value.
        If not, gets the property through the api.

        Args:
            prop_key: Name or id of the property to retrieve.
            cache: Boolean to decide whether to return the info from the page
                or query the API again.
            safety_off: If `True` will use cached values of rollups and
                formulas
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
    ) -> Union[PropertyValue, AsyncPropertyItemIterator]:
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

    def _get_prop_name(self, prop_key: str) -> Optional[str]:
        """Gets propetry name from property key.

        Args:
            prop_key: Either a property name or property id.

        Returns:
            Property name or `None` if key is invalid.
        """
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
