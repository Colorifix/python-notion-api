from copy import copy

from pytest import mark
from pytest_asyncio import fixture as async_fixture

from python_notion_api.async_api.notion_block import NotionBlock
from python_notion_api.models import ParagraphBlock, RichTextObject

TEST_BLOCK_ID = "f572e889cd374edbbd15d8bf13174bbc"


@mark.asyncio
class TestAsyncBlock:
    @async_fixture
    async def block(self, async_api):
        block = NotionBlock(block_id=TEST_BLOCK_ID, api=async_api)
        await block.reload()
        return block

    async def test_async_block(block):
        assert block is not None

    async def test_add_children(self, block):
        new_block = ParagraphBlock.from_str("Added block text")
        await block.add_child_block(content=[new_block], reload_block=True)
        await block.reload()
        assert block._object.has_children

    async def test_set_block(self, block):
        new_object = copy(block._object)
        new_object.paragraph.rich_text[0] = RichTextObject.from_str(
            "New block"
        )
        await block.set(block=new_object, reload_block=True)
        await block.reload()
        assert block._object.paragraph.rich_text[0].plain_text == "New block"
