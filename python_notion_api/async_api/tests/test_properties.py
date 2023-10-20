import unittest
import os

from python_notion_api import File

from python_notion_api.async_api import AsyncNotionAPI

from python_notion_api.models.filters import (
    and_filter, or_filter,
    SelectFilter, MultiSelectFilter
)

from python_notion_api.models.sorts import Sort

from datetime import datetime


class _TestBase(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.api = AsyncNotionAPI(access_token=os.environ.get("NOTION_TOKEN"))
        cls.TEST_DB = "401076f6c7c04ae796bf3e4c847361e1"

        cls.TEST_TITLE = f"API Test {datetime.utcnow().isoformat()}"
        cls.TEST_TEXT = "Test text is boring"
        cls.TEST_NUMBER = 12.5
        cls.TEST_SELECT = "foo"
        cls.TEST_STATUS = "In progress"
        cls.TEST_MULTI_SELECT = ["foo", "bar", "baz"]
        cls.TEST_DATE = datetime.now()
        cls.TEST_PEOPLE = ["fa9e1df9-7c24-427c-9c20-eac629565fe4"]
        cls.TEST_FILES = [File(name="foo.pdf", url="http://example.com/file")]
        cls.TEST_CHECKBOX = True
        cls.TEST_URL = "http://example.com"
        cls.TEST_EMAIL = "test@example.com"
        cls.TEST_PHONE = "079847364088"


class TestCore(_TestBase):
    async def test_get_database(self):
        db = await self.api.get_database(database_id=self.TEST_DB)
        self.assertEqual(db.database_id, self.TEST_DB)

    async def test_create_empty_page(self):
        db = await self.api.get_database(database_id=self.TEST_DB)
        new_page = await db.create_page()
        self.assertIsNotNone(new_page)

    async def test_create_empty_page_with_cover(self):
        db = await self.api.get_database(database_id=self.TEST_DB)
        new_page = await db.create_page(
            cover_url=(
                "https://images.unsplash.com/"
                "photo-1514888286974-6c03e2ca1dba?ixlib=rb-1.2.1&"
                "ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8"
                "&auto=format&fit=crop&w=2286&q=80"
            )
        )
        self.assertIsNotNone(new_page)

    async def test_get_page(self):
        test_page = 'e439b7a7296d45b98805f24c9cfc2115'
        page = await self.api.get_page(page_id=test_page)
        page_dict = await page.to_dict()
        self.assertIsInstance(page_dict, dict)


class TestPage(_TestBase):

    @classmethod
    async def get_db(cls):
        if not hasattr(cls, 'db'):
            cls.db = await cls.api.get_database(database_id=cls.TEST_DB)

    @classmethod
    async def get_page(cls):
        if not hasattr(cls, 'page'):
            cls.page = await cls.db.create_page()

    async def asyncSetUp(self):
        await self.get_db()
        await self.get_page()

    async def test_set_title(self):
        await self.page.set("Name", self.TEST_TITLE)
        self.assertEqual(
            await self.page.get("Name", cache=False), self.TEST_TITLE
        )

    async def test_set_text(self):
        await self.page.set("Text", self.TEST_TEXT)
        self.assertEqual(
            await self.page.get("Text", cache=False), self.TEST_TEXT
        )

    async def test_set_number(self):
        await self.page.set("Number", self.TEST_NUMBER)
        self.assertEqual(
            await self.page.get("Number", cache=False),
            self.TEST_NUMBER
        )

    async def test_set_select(self):
        await self.page.set("Select", self.TEST_SELECT)
        self.assertEqual(
            await self.page.get("Select", cache=False), self.TEST_SELECT
        )

    async def test_set_status(self):
        await self.page.set("Status", self.TEST_STATUS)
        self.assertEqual(
            await self.page.get("Status", cache=False), self.TEST_STATUS
        )

    async def test_set_multi_select(self):
        await self.page.set("Multi-select", self.TEST_MULTI_SELECT)
        self.assertEqual(
            await self.page.get("Multi-select", cache=False),
            self.TEST_MULTI_SELECT
        )

    async def test_set_date(self):
        await self.page.set("Date", self.TEST_DATE)
        self.assertTrue(
            abs(
                (await self.page.get("Date", cache=False)).start.timestamp()
                - self.TEST_DATE.timestamp()
            ) < 60000
        )

    async def test_set_person(self):
        await self.page.set("Person", self.TEST_PEOPLE)
        self.assertEqual(
            await self.page.get("Person", cache=False),
            ["Mihails Delmans"]
        )

    async def test_set_files(self):
        await self.page.set("Files & media", self.TEST_FILES)
        self.assertEqual(
            (await self.page.get("Files & media", cache=False))[0].url,
            self.TEST_FILES[0].url
        )

    async def test_set_checkbox(self):
        await self.page.set("Checkbox", self.TEST_CHECKBOX)
        self.assertEqual(
            await self.page.get("Checkbox", cache=False),
            self.TEST_CHECKBOX
        )

    async def test_set_url(self):
        await self.page.set("URL", self.TEST_URL)
        self.assertEqual(
            await self.page.get("URL", cache=False),
            self.TEST_URL
        )

    async def test_set_email(self):
        await self.page.set("Email", self.TEST_EMAIL)
        self.assertEqual(
            await self.page.get("Email", cache=False),
            self.TEST_EMAIL
        )

    async def test_set_phone(self):
        await self.page.set("Phone", self.TEST_PHONE)
        self.assertEqual(
            await self.page.get("Phone", cache=False),
            self.TEST_PHONE
        )

    async def test_set_relation(self):
        await self.page.set("Relation", [self.page.page_id])
        self.assertEqual(
            (await self.page.get(
                            "Relation", cache=False
                        ))[0].replace('-', ''),
            self.page.page_id
        )

    async def test_create_new_page(self):
        new_page = await self.db.create_page(
            properties={
                "Name": self.TEST_TITLE,
                "Text": self.TEST_TEXT,
                "Number": self.TEST_NUMBER,
                "Select": self.TEST_SELECT,
                "Multi-select": self.TEST_MULTI_SELECT,
                "Status": self.TEST_STATUS,
                "Date": self.TEST_DATE,
                "Person": self.TEST_PEOPLE,
                "Files & media": self.TEST_FILES,
                "Checkbox": self.TEST_CHECKBOX,
                "URL": self.TEST_URL,
                "Email": self.TEST_EMAIL,
                "Phone": self.TEST_PHONE
            }
        )
        self.assertIsNotNone(new_page)

    async def test_get_unique_id(self):
        unique_id = await self.page.get('Unique ID')
        self.assertIsInstance(unique_id, int)

    async def test_get_by_id(self):
        await self.page.set('Email', self.TEST_EMAIL)
        email = await self.page.get('%3E%5Ehh', cache=False)
        self.assertEqual(email, self.TEST_EMAIL)

    async def test_set_by_id(self):
        await self.page.set('%3E%5Ehh', self.TEST_EMAIL)
        email = await self.page.get('Email', cache=False)
        self.assertEqual(email, self.TEST_EMAIL)

    async def test_update(self):
        await self.page.update(
            properties={
                '%3E%5Ehh': self.TEST_EMAIL,
                'Phone': self.TEST_PHONE
            }
        )

        email = await self.page.get('Email', cache=False)
        phone = await self.page.get('Phone', cache=False)

        self.assertEqual(email, self.TEST_EMAIL)
        self.assertEqual(phone, self.TEST_PHONE)

    async def test_reload(self):
        await self.page.set('Email', self.TEST_EMAIL)
        await self.page.reload()

        email = await self.page.get('Email', cache=True)
        self.assertEqual(email, self.TEST_EMAIL)


class TestRollups(_TestBase):
    number_page_id = "25e800a118414575ab30a8dc42689b74"
    date_page_id = "e38bb90faf8a436895f089fed2446cc6"
    empty_rollup_page_id = "2b5efae5bad24df884b4f953e3788b64"

    async def test_number_rollup(self):
        number_page = await self.api.get_page(self.number_page_id)

        num = await number_page.get("Number rollup")
        self.assertEqual(num, 10)

    async def test_date_rollup(self):
        date_page = await self.api.get_page(self.date_page_id)

        date = await date_page.get("Date rollup")

        self.assertIsInstance(date.start, datetime)

    async def test_empty_rollup(self):
        page = await self.api.get_page(self.empty_rollup_page_id)
        num = await page.get("Number rollup")

        self.assertIsNone(num)


class TestDatabase(_TestBase):

    @classmethod
    async def get_db(cls):
        if not hasattr(cls, 'db'):
            cls.db = await cls.api.get_database(database_id=cls.TEST_DB)

    async def asyncSetUp(self):
        await self.get_db()

    async def test_query_database(self):
        pages = self.db.query()

    async def test_prop_filter(self):
        pages = self.db.query(
            filters=SelectFilter(property="Select", equals=self.TEST_SELECT)
        )
        page = await anext(pages)
        value = await page.get("Select")
        self.assertEqual(value, self.TEST_SELECT)

    async def test_and_filter(self):
        pages = self.db.query(
            filters=and_filter(
                [
                    SelectFilter(property="Select", equals=self.TEST_SELECT),
                    MultiSelectFilter(property="Multi-select", contains="bar")
                ]
            )
        )
        page = await anext(pages)
        value = await page.get("Select")
        self.assertEqual(value, self.TEST_SELECT)

    async def test_or_filter(self):
        pages = self.db.query(
            filters=or_filter(
                [
                    SelectFilter(property="Select", equals=self.TEST_SELECT),
                    MultiSelectFilter(property="Multi-select", contains="bar")
                ]
            )
        )
        page = await anext(pages)
        value = await page.get("Select")
        self.assertEqual(value, self.TEST_SELECT)

    async def test_sort(self):
        pages = self.db.query(
            sorts=[Sort(property="Date")]
        )
        page = await anext(pages)
        self.assertIsNotNone(page)

    async def test_descending_sort(self):
        pages = self.db.query(
            sorts=[Sort(property="Date", descending=True)]
        )
        page = await anext(pages)
        self.assertIsNotNone(page)


if __name__ == '__main__':
    unittest.main()
