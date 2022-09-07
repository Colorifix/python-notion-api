import unittest
import os

from notion_integration.api import NotionAPI, File
from notion_integration.api.models.filters import (
    and_filter, or_filter,
    SelectFilter, MultiSelectFilter
)

from notion_integration.api.models.sorts import Sort

from datetime import datetime


class _TestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.api = NotionAPI(access_token=os.environ.get("NOTION_SECRET"))
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
        cls.TEST_URL = "http://colorifix.com"
        cls.TEST_EMAIL = "admin@colorifix.com"
        cls.TEST_PHONE = "079847364088"

        cls.extra_setup()

    @classmethod
    def extra_setup(cls):
        pass


class TestCore(_TestBase):
    def test_get_database(self):
        db = self.api.get_database(database_id=self.TEST_DB)
        self.assertEqual(db.database_id, self.TEST_DB)

    def test_create_empty_page(self):
        db = self.api.get_database(database_id=self.TEST_DB)
        new_page = db.create_page()
        self.assertIsNotNone(new_page)

    def test_create_empty_page_with_cover(self):
        db = self.api.get_database(database_id=self.TEST_DB)
        new_page = db.create_page(
            cover_url=(
                "https://images.unsplash.com/"
                "photo-1514888286974-6c03e2ca1dba?ixlib=rb-1.2.1&"
                "ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8"
                "&auto=format&fit=crop&w=2286&q=80"
            )
        )
        self.assertIsNotNone(new_page)

    def test_get_page(self):
        test_page = 'e439b7a7296d45b98805f24c9cfc2115'
        page = self.api.get_page(page_id=test_page)
        self.assertIsInstance(page.to_dict(), dict)


class TestPage(_TestBase):
    @classmethod
    def extra_setup(cls):
        cls.db = cls.api.get_database(database_id=cls.TEST_DB)

        cls.new_page = cls.db.create_page()

    def test_set_title(self):
        self.new_page.set("Name", self.TEST_TITLE)
        self.assertEqual(self.new_page.get("Name").value, self.TEST_TITLE)

    def test_set_text(self):
        self.new_page.set("Text", self.TEST_TEXT)
        self.assertEqual(self.new_page.get("Text").value, self.TEST_TEXT)

    def test_set_number(self):
        self.new_page.set("Number", self.TEST_NUMBER)
        self.assertEqual(self.new_page.get("Number").value, self.TEST_NUMBER)

    def test_set_select(self):
        self.new_page.set("Select", self.TEST_SELECT)
        self.assertEqual(self.new_page.get("Select").value, self.TEST_SELECT)

    def test_set_status(self):
        self.new_page.set("Status", self.TEST_STATUS)
        self.assertEqual(self.new_page.get("Status").value, self.TEST_STATUS)

    def test_set_multi_select(self):
        self.new_page.set("Multi-select", self.TEST_MULTI_SELECT)
        self.assertEqual(
            self.new_page.get("Multi-select").value,
            self.TEST_MULTI_SELECT
        )

    def test_set_date(self):
        self.new_page.set("Date", self.TEST_DATE)
        self.assertTrue(
            abs(
                self.new_page.get("Date").value.start.timestamp()
                - self.TEST_DATE.timestamp()
            ) < 60000
        )

    def test_set_person(self):
        self.new_page.set("Person", self.TEST_PEOPLE)
        self.assertEqual(
            self.new_page.get("Person").value,
            ["Mihails Delmans"]
        )

    def test_set_files(self):
        self.new_page.set("Files & media", self.TEST_FILES)
        self.assertEqual(
            self.new_page.get("Files & media").value[0].url,
            self.TEST_FILES[0].url
        )

    def test_set_checkbox(self):
        self.new_page.set("Checkbox", self.TEST_CHECKBOX)
        self.assertEqual(
            self.new_page.get("Checkbox").value,
            self.TEST_CHECKBOX
        )

    def test_set_url(self):
        self.new_page.set("URL", self.TEST_URL)
        self.assertEqual(self.new_page.get("URL").value, self.TEST_URL)

    def test_set_email(self):
        self.new_page.set("Email", self.TEST_EMAIL)
        self.assertEqual(self.new_page.get("Email").value, self.TEST_EMAIL)

    def test_set_phone(self):
        self.new_page.set("Phone", self.TEST_PHONE)
        self.assertEqual(self.new_page.get("Phone").value, self.TEST_PHONE)

    def test_set_relation(self):
        self.new_page.set("Relation", [self.new_page.page_id])
        self.assertEqual(
            self.new_page.get("Relation").value[0],
            self.new_page.page_id
        )

    def test_create_new_page(self):
        new_page = self.db.create_page(
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


class TestRollups(_TestBase):
    @classmethod
    def extra_setup(cls):
        cls.number_page_id = "25e800a118414575ab30a8dc42689b74"
        cls.date_page_id = "e38bb90faf8a436895f089fed2446cc6"

    def test_number_rollup(self):
        number_page = self.api.get_page(self.number_page_id)

        num = number_page.get("Number rollup")
        self.assertEqual(num.value, 10)

    def test_date_rollup(self):
        date_page = self.api.get_page(self.date_page_id)

        date = date_page.get("Date rollup")
        self.assertIsInstance(date.value.start, datetime)


class TestDatabase(_TestBase):
    @classmethod
    def extra_setup(cls):
        cls.db = cls.api.get_database(database_id=cls.TEST_DB)

    def test_query_database(self):
        pages = self.db.query()

    def test_prop_filter(self):
        pages = self.db.query(
            filters=SelectFilter(property="Select", equals=self.TEST_SELECT)
        )
        page = next(pages)
        self.assertEqual(page.get("Select").value, self.TEST_SELECT)

    def test_and_filter(self):
        pages = self.db.query(
            filters=and_filter(
                [
                    SelectFilter(property="Select", equals=self.TEST_SELECT),
                    MultiSelectFilter(property="Multi-select", contains="bar")
                ]
            )
        )
        page = next(pages)
        self.assertEqual(page.get("Select").value, self.TEST_SELECT)

    def test_or_filter(self):
        pages = self.db.query(
            filters=or_filter(
                [
                    SelectFilter(property="Select", equals=self.TEST_SELECT),
                    MultiSelectFilter(property="Multi-select", contains="bar")
                ]
            )
        )
        page = next(pages)
        self.assertEqual(page.get("Select").value, self.TEST_SELECT)

    def test_sort(self):
        pages = self.db.query(
            sorts=[Sort(property="Date")]
        )
        page = next(pages)
        self.assertIsNotNone(page)

    def test_descending_sort(self):
        pages = self.db.query(
            sorts=[Sort(property="Date", descending=True)]
        )
        page = next(pages)
        self.assertIsNotNone(page)