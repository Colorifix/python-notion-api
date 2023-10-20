import os
import unittest
import random

from python_notion_api.async_api import (
    AsyncNotionAPI,
    NotionPage,
    NotionDatabase
)

TEST_DATABASE_ID = "401076f6c7c04ae796bf3e4c847361e1"


class TestAsyncDatabase(unittest.IsolatedAsyncioTestCase):
    def get_api(self):
        return AsyncNotionAPI(access_token=os.environ["NOTION_TOKEN"])

    async def get_database(self):
        api = self.get_api()
        database = NotionDatabase(database_id=TEST_DATABASE_ID, api=api)
        await database.reload()

        return database

    async def test_load_database(self):
        database = await self.get_database()

        self.assertIsNotNone(database)

        self.assertIsNotNone(database._object)

        self.assertIsNotNone(database.title)
        self.assertIsNotNone(database.properties)
        self.assertIsNotNone(database.relations)

    async def test_create_database_page(self):
        database = await self.get_database()

        new_page = await database.create_page(
            properties={}
        )

        self.assertIsInstance(new_page, NotionPage)
        self.assertIsNotNone(new_page._object)

    async def test_create_database_page_with_properties(self):
        database = await self.get_database()

        properties = {
            "Text": "".join([random.choice('abcd') for _ in range(10)]),
            "Number": int(
                "".join([random.choice('1234') for _ in range(3)])
            )
        }

        new_page = await database.create_page(
            properties=properties
        )

        self.assertEqual(await new_page.get('Text'), properties['Text'])
        self.assertEqual(await new_page.get('Number'), properties['Number'])

    async def test_query_database(self):
        database = await self.get_database()
        pages = database.query()

        page = await anext(pages)
        self.assertIsInstance(page, NotionPage)

    async def test_get_object_property(self):
        database = await self.get_database()

        created_time = database.created_time

        self.assertIsNotNone(created_time)

    async def test_get_title(self):
        database = await self.get_database()

        title = database.title

        self.assertIsNotNone(title)

    async def test_get_properties(self):
        database = await self.get_database()

        properties = database.properties

        self.assertIsInstance(properties, dict)

    async def test_get_relations(self):
        database = await self.get_database()

        relations = database.relations

        self.assertIsInstance(relations, dict)

        for _, relation in relations.items():
            self.assertEqual(relation.config_type, 'relation')


if __name__ == "__main__":
    unittest.main()
