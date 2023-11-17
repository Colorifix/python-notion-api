from pytest import mark
from pytest_asyncio import fixture as async_fixture

from python_notion_api.async_api.notion_block import NotionBlock
from python_notion_api.async_api.notion_database import NotionDatabase
from python_notion_api.async_api.notion_page import NotionPage

TEST_DATABASE_ID = "401076f6c7c04ae796bf3e4c847361e1"
TEST_BLOCK_ID = "f572e889cd374edbbd15d8bf13174bbc"


@async_fixture
async def page(async_api, example_page_id_2):
    return await async_api.get_page(page_id=example_page_id_2)


@async_fixture
async def database(async_api):
    return await async_api.get_database(database_id=TEST_DATABASE_ID)


@async_fixture
async def block(async_api):
    return await async_api.get_block(block_id=TEST_BLOCK_ID)


@mark.asyncio
class TestAsyncAPI:
    async def test_api_is_valid(self, async_api):
        assert async_api is not None

    async def test_page_is_valid(self, page):
        assert isinstance(page, NotionPage)
        assert page._object is not None
        assert isinstance(page.database, NotionDatabase)

    async def test_database_is_valid(self, database):
        assert isinstance(database, NotionDatabase)
        assert database._object is not None
        assert database._properties is not None
        assert database._title is not None

    async def test_block_is_valid(self, block):
        assert isinstance(block, NotionBlock)
        assert block._object is not None

    async def test_me_is_valid(self, async_api):
        me = await async_api.me()
        assert me is not None
