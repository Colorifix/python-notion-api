import os
import unittest
from copy import copy

from python_notion_api.async_api import (
    AsyncNotionAPI,
    NotionBlock
)


TEST_BLOCK_ID = "f572e889cd374edbbd15d8bf13174bbc"


class TestAsyncBlock(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.api = AsyncNotionAPI(access_token=os.environ["NOTION_TOKEN"])
        self.assertIsNotNone(self.api)

        self.block = NotionBlock(block_id=TEST_BLOCK_ID, api=self.api)
        await self.block.reload()
        self.assertIsNotNone(self.block)

    async def test_add_children(self):
        await self.block.add_child_block(
            content=[self.block._object],
            reload_block=True
        )

        self.assertTrue(self.block.has_children)

    async def test_set_block(self):
        new_object = copy(self.block._object)
        new_object.paragraph.rich_text[0].plain_text = "New block"
        new_object.created_time = None

        await self.block.set(
            block=new_object,
            reload_block=True
        )


if __name__ == "__main__":
    unittest.main()
