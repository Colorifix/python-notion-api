import os
import unittest
import random

from python_notion_api.async_api import (
    AsyncNotionAPI,
    NotionPage,
    AsyncPropertyItemIterator
)

from python_notion_api import PropertyValue

TEST_PAGE_ID = "d5bce0a0fe6248d0a120c6c693d9b597"


class TestAsyncPage(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.api = AsyncNotionAPI(access_token=os.environ["NOTION_TOKEN"])
        self.assertIsNotNone(self.api)

        self.page = NotionPage(page_id=TEST_PAGE_ID, api=self.api)
        await self.page.reload()
        self.assertIsNotNone(self.page)
        self.assertIsNotNone(self.page._object)

    async def test_get_object_property(self):
        created_time = self.page.created_time

        self.assertIsNotNone(created_time)

    async def test_get_page_property(self):
        status = await self.page.get('Status')

        self.assertIsInstance(status, str)

    async def test_get_invalid_page_property(self):
        with self.assertRaises(ValueError):
            await self.page.get('status')

    async def test_get_page_property_raw(self):

        status = await self.page.get('Status', raw=True)

        self.assertIsInstance(status, PropertyValue)

    async def test_set_page_property(self):

        status_cache = await self.page.get('Status')

        await self.page.set('Status', 'Done')

        new_status = await self.page.get('Status', cache=False)

        await self.page.set('Status', status_cache)

        self.assertEqual(new_status, 'Done')
        self.assertNotEqual(status_cache, 'Done')

    async def test_page_alive(self):

        await self.page.unarchive()
        await self.page.reload()
        self.assertTrue(self.page.is_alive)

        await self.page.archive()
        await self.page.reload()
        self.assertFalse(self.page.is_alive)

        await self.page.unarchive()
        await self.page.reload()
        self.assertTrue(self.page.is_alive)

    async def test_update_page(self):
        properties = {
            "Text": "".join([random.choice('abcd') for _ in range(10)]),
            "Number": int(
                "".join([random.choice('1234') for _ in range(3)])
            )
        }

        await self.page.update(properties=properties, reload_page=True)

        self.assertEqual(await self.page.get('Text'), properties['Text'])
        self.assertEqual(await self.page.get('Number'), properties['Number'])

    async def test_get_properties(self):
        properties = await self.page.get_properties()

        self.assertIsInstance(properties, dict)

    async def test_get_properties_raw(self):
        properties = await self.page.get_properties(raw=True)

        self.assertIsInstance(properties, dict)
        for key, value in properties.items():
            self.assertTrue(
                isinstance(value, PropertyValue)
                or isinstance(value, AsyncPropertyItemIterator)
            )

    async def test_page_to_dict(self):
        dict_props = await self.page.to_dict()

        self.assertIsInstance(dict_props, dict)

    async def test_blocks(self):
        blocks = [block async for block in await self.page.get_blocks()]

        await self.page.add_blocks(blocks=[blocks[0]])


if __name__ == "__main__":
    unittest.main()
