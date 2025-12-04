import random

from pytest import mark
from pytest_asyncio import fixture as async_fixture

from python_notion_api.async_api.notion_data_source import NotionDataSource
from python_notion_api.async_api.notion_page import NotionPage

TEST_DATA_SOURCE_ID = "924fbc0cb38f4a09ac2f967266f5c743"


@mark.asyncio
class TestAsyncDataSource:
    @async_fixture
    async def data_source(self, async_api):
        data_source = NotionDataSource(
            data_source_id=TEST_DATA_SOURCE_ID, api=async_api
        )
        await data_source.reload()
        return data_source

    async def test_load_data_source(self, data_source):
        assert data_source is not None
        assert data_source._object is not None
        assert data_source.title is not None
        assert data_source.properties is not None
        assert data_source.relations is not None

    async def test_create_data_source_page(self, data_source):
        new_page = await data_source.create_page(properties={})
        assert isinstance(new_page, NotionPage)
        assert new_page._object is not None

    async def test_create_data_source_page_with_properties(self, data_source):
        properties = {
            "Text": "".join([random.choice("abcd") for _ in range(10)]),
            "Number": int("".join([random.choice("1234") for _ in range(3)])),
        }
        new_page = await data_source.create_page(properties=properties)

        assert await new_page.get("Text") == properties["Text"]
        assert await new_page.get("Number") == properties["Number"]

    async def test_query_data_source(self, data_source):
        pages = data_source.query()
        page = await anext(pages)
        assert isinstance(page, NotionPage)

    async def test_get_object_property(self, data_source):
        created_time = data_source.created_time
        assert created_time is not None

    async def test_get_title(self, data_source):
        title = data_source.title
        assert title is not None

    async def test_get_properties(self, data_source):
        properties = data_source.properties
        assert isinstance(properties, dict)

    async def test_get_relations(self, data_source):
        relations = data_source.relations
        assert isinstance(relations, dict)

        for _, relation in relations.items():
            assert relation.config_type == "relation"
