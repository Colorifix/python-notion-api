from pytest import mark
from pytest_asyncio import fixture as async_fixture

from python_notion_api.async_api.notion_database import NotionDatabase
from python_notion_api.models.common import DataSourceObject


@mark.asyncio
class TestAsyncDatabase:
    @async_fixture
    async def database(self, async_api, database_id):
        database = NotionDatabase(database_id=database_id, api=async_api)
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

    async def test_get_data_sources(
        self, database, data_source_id1, data_source_id2
    ):
        data_sources = database.data_sources
        assert isinstance(data_sources, list)

        data_sources.sort(key=lambda x: x.data_source_id)

        assert len(data_sources) == 2
        assert isinstance(data_sources[0], DataSourceObject)
        assert (
            data_sources[0].data_source_id.replace("-", "") == data_source_id2
        )
        assert data_sources[0].data_source_name is not None
        assert isinstance(data_sources[1], DataSourceObject)
        assert (
            data_sources[1].data_source_id.replace("-", "") == data_source_id1
        )
        assert data_sources[1].data_source_name is not None
