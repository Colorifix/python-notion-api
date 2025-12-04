from pytest import mark
from pytest_asyncio import fixture as async_fixture

from python_notion_api.async_api.notion_database import NotionDatabase
from python_notion_api.models.common import DataSourceObject

TEST_DATABASE_ID = "401076f6c7c04ae796bf3e4c847361e1"
TEST_DATA_SOURCE_IDS = [
    "28d751c8a89180ed80c8000b05bd4bb1",
    "924fbc0cb38f4a09ac2f967266f5c743",
]


@mark.asyncio
class TestAsyncDatabase:
    @async_fixture
    async def database(self, async_api):
        database = NotionDatabase(database_id=TEST_DATABASE_ID, api=async_api)
        await database.reload()
        return database

    async def test_load_database(self, database):
        assert database is not None
        assert database._object is not None
        assert database.title is not None
        assert database.data_sources is not None

    async def test_get_object_property(self, database):
        created_time = database.created_time
        assert created_time is not None

    async def test_get_title(self, database):
        title = database.title
        assert title is not None

    async def test_get_data_sources(self, database):
        data_sources = database.data_sources
        assert isinstance(data_sources, list)

        data_sources.sort(key=lambda x: x.data_source_id)

        for i, data_source in enumerate(data_sources):
            assert isinstance(data_source, DataSourceObject)
            assert (
                data_source.data_source_id.replace("-", "")
                == TEST_DATA_SOURCE_IDS[i]
            )
            assert data_source.data_source_name is not None
