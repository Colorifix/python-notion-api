import random

import pytest
from pytest import mark
from pytest_asyncio import fixture as async_fixture

from python_notion_api import PropertyValue
from python_notion_api.async_api import AsyncPropertyItemIterator, NotionPage


@mark.asyncio
class TestAsyncPage:
    @async_fixture
    async def page(self, async_api, example_page_id_2):
        async_page = NotionPage(page_id=example_page_id_2, api=async_api)
        await async_page.reload()
        return async_page

    async def test_page_is_valid(self, page):
        assert page is not None
        assert page._object is not None

    async def test_get_object_property(self, page):
        created_time = page.created_time
        assert created_time is not None

    async def test_get_page_property(self, page):
        status = await page.get("Status")
        assert isinstance(status, str)

    async def test_get_invalid_page_property(self, page):
        with pytest.raises(ValueError) as exc:
            await page.get("status")
        assert "Invalid property key" in str(exc.value)

    async def test_get_page_property_raw(self, page):
        status = await page.get("Status", raw=True)
        assert isinstance(status, PropertyValue)

    async def test_set_page_property(self, page):
        status_cache = await page.get("Status")
        await page.set("Status", "Done")
        new_status = await page.get("Status", cache=False)
        await page.set("Status", status_cache)

        assert new_status == "Done"
        assert status_cache != "Done"

    async def test_page_alive(self, page):
        await page.unarchive()
        await page.reload()
        assert page.is_alive

        await page.archive()
        await page.reload()
        assert not page.is_alive

        await page.unarchive()
        await page.reload()
        assert page.is_alive

    async def test_update_page(self, page):
        properties = {
            "Text": "".join([random.choice("abcd") for _ in range(10)]),
            "Number": int("".join([random.choice("1234") for _ in range(3)])),
        }
        await page.update(properties=properties, reload_page=True)

        assert await page.get("Text") == properties["Text"]
        assert await page.get("Number") == properties["Number"]

    async def test_get_properties(self, page):
        properties = await page.get_properties()
        assert isinstance(properties, dict)

    async def test_get_properties_raw(self, page):
        properties = await page.get_properties(raw=True)

        assert isinstance(properties, dict)
        for _, value in properties.items():
            assert isinstance(value, PropertyValue) or isinstance(
                value, AsyncPropertyItemIterator
            )

    async def test_page_to_dict(self, page):
        dict_props = await page.to_dict()
        assert isinstance(dict_props, dict)

    async def test_blocks(self, page):
        blocks = [block async for block in await page.get_blocks()]
        await page.add_blocks(blocks=[blocks[0]])
