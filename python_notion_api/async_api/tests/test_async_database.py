import random

from pytest import mark
from pytest_asyncio import fixture as async_fixture

from python_notion_api.async_api.notion_database import NotionDatabase
from python_notion_api.async_api.notion_page import NotionPage

TEST_DATABASE_ID = "401076f6c7c04ae796bf3e4c847361e1"


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
        assert database.properties is not None
        assert database.relations is not None

    async def test_create_database_page(self, database):
        new_page = await database.create_page(properties={})
        assert isinstance(new_page, NotionPage)
        assert new_page._object is not None

    async def test_create_database_page_with_properties(self, database):
        properties = {
            "Text": "".join([random.choice("abcd") for _ in range(10)]),
            "Number": int("".join([random.choice("1234") for _ in range(3)])),
        }
        new_page = await database.create_page(properties=properties)

        assert await new_page.get("Text") == properties["Text"]
        assert await new_page.get("Number") == properties["Number"]

    async def test_query_database(self, database):
        pages = database.query()
        page = await anext(pages)
        assert isinstance(page, NotionPage)

    async def test_get_object_property(self, database):
        created_time = database.created_time
        assert created_time is not None

    async def test_get_title(self, database):
        title = database.title
        assert title is not None

    async def test_get_properties(self, database):
        properties = database.properties
        assert isinstance(properties, dict)

    async def test_get_relations(self, database):
        relations = database.relations
        assert isinstance(relations, dict)

        for _, relation in relations.items():
            assert relation.config_type == "relation"
