import os
import unittest

from python_notion_api.async_api import (
    AsyncNotionAPI,
    NotionPage,
    NotionBlock,
    NotionDatabase
)

TEST_PAGE_ID = "d5bce0a0fe6248d0a120c6c693d9b597"
TEST_DATABASE_ID = "401076f6c7c04ae796bf3e4c847361e1"
TEST_BLOCK_ID = "f572e889cd374edbbd15d8bf13174bbc"


class TestAsyncAPI(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.api = AsyncNotionAPI(access_token=os.environ["NOTION_TOKEN"])
        self.assertIsNotNone(self.api)

    async def test_get_page(self):
        page = await self.api.get_page(page_id=TEST_PAGE_ID)

        self.assertIsInstance(page, NotionPage)
        self.assertIsNotNone(page._object)
        self.assertIsInstance(page.database, NotionDatabase)

    async def test_get_database(self):
        database = await self.api.get_database(database_id=TEST_DATABASE_ID)

        self.assertIsInstance(database, NotionDatabase)
        self.assertIsNotNone(database._object)
        self.assertIsNotNone(database._properties)
        self.assertIsNotNone(database._title)

    async def test_get_block(self):
        block = await self.api.get_block(block_id=TEST_BLOCK_ID)

        self.assertIsInstance(block, NotionBlock)
        self.assertIsNotNone(block._object)

    async def get_me(self):

        me = await self.api.me()

        self.assertIsNotNone(me)


if __name__ == "__main__":
    unittest.main()
