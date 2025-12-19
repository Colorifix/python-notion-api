from pytest import mark
from pytest_asyncio import fixture as async_fixture

from python_notion_api.async_api.notion_block import NotionBlock
from python_notion_api.async_api.notion_data_source import NotionDataSource
from python_notion_api.async_api.notion_database import NotionDatabase
from python_notion_api.async_api.notion_page import NotionPage


@async_fixture
async def page(async_api, example_page_id):
    return await async_api.get_page(page_id=example_page_id)


@async_fixture
async def database(async_api, database_id):
    return await async_api.get_database(database_id=database_id)


@async_fixture
async def data_source(async_api, data_source_id1):
    return await async_api.get_data_source(data_source_id=data_source_id1)


@async_fixture
async def block(async_api, block_id):
    return await async_api.get_block(block_id=block_id)


@mark.asyncio
class TestAsyncAPI:
    async def test_api_is_valid(self, async_api):
        assert async_api is not None

    async def test_page_is_valid(self, page):
        assert isinstance(page, NotionPage)
        assert page._object is not None
        assert isinstance(page.data_source, NotionDataSource)

    async def test_database_is_valid(self, database):
        assert isinstance(database, NotionDatabase)
        assert database._object is not None
        assert database._data_sources is not None
        assert database._title is not None

    async def test_data_source_is_valid(self, data_source):
        assert isinstance(data_source, NotionDataSource)
        assert data_source._object is not None
        assert data_source._properties is not None
        assert data_source._title is not None

    async def test_block_is_valid(self, block):
        assert isinstance(block, NotionBlock)
        assert block._object is not None

    async def test_me_is_valid(self, async_api):
        me = await async_api.me()
        assert me is not None
