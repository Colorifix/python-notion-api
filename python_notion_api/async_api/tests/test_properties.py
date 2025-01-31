import asyncio
import os
from datetime import UTC, datetime

from pytest import fixture, mark
from pytest_asyncio import fixture as async_fixture

from python_notion_api import File
from python_notion_api.async_api.api import AsyncNotionAPI
from python_notion_api.models.filters import (
    MultiSelectFilter,
    SelectFilter,
    and_filter,
    or_filter,
)
from python_notion_api.models.sorts import Sort

TEST_DB = "401076f6c7c04ae796bf3e4c847361e1"
TEST_TITLE = f"API Test {datetime.now(UTC).isoformat()}"
TEST_TEXT = "Test text is boring"
TEST_NUMBER = 12.5
TEST_SELECT = "foo"
TEST_STATUS = "In progress"
TEST_MULTI_SELECT = ["foo", "bar", "baz"]
TEST_DATE = datetime.now()
TEST_PEOPLE = ["fa9e1df9-7c24-427c-9c20-eac629565fe4"]
TEST_FILES = [File(name="foo.pdf", url="http://example.com/file")]
TEST_CHECKBOX = True
TEST_URL = "http://example.com"
TEST_EMAIL = "test@example.com"
TEST_PHONE = "079847364088"


@async_fixture
async def database(async_api):
    return await async_api.get_database(database_id=TEST_DB)


@mark.asyncio
class TestCore:
    async def test_get_database(self, database):
        assert database.database_id == TEST_DB

    async def test_create_empty_page(self, database):
        new_page = await database.create_page()
        assert new_page is not None

    async def test_create_empty_page_with_cover(self, database, cover_url):
        new_page = await database.create_page(cover_url=cover_url)
        assert new_page is not None

    async def test_get_page(self, async_api, example_page_id):
        page = await async_api.get_page(page_id=example_page_id)
        page_dict = await page.to_dict()
        assert isinstance(page_dict, dict)


@mark.asyncio
class TestPage:
    @fixture(scope="class")
    def event_loop(cls):
        loop = asyncio.get_event_loop()
        yield loop
        loop.close()

    @async_fixture(scope="class")
    def api(cls):
        if not hasattr(cls, "async_api"):
            cls.async_api = AsyncNotionAPI(
                access_token=os.environ.get("NOTION_TOKEN")
            )
        return cls.async_api

    @async_fixture(scope="class")
    async def database(cls, api):
        if not hasattr(cls, "async_database"):
            cls.async_database = await cls.async_api.get_database(
                database_id=TEST_DB
            )
        return cls.async_database

    @async_fixture(scope="class")
    async def page(cls, database):
        if not hasattr(cls, "async_page"):
            cls.async_page = await cls.async_database.create_page()
        return cls.async_page

    @mark.parametrize(
        "property,value",
        [
            ["Name", TEST_TITLE],
            ["Text", TEST_TEXT],
            ["Number", TEST_NUMBER],
            ["Select", TEST_SELECT],
            ["Status", TEST_STATUS],
            ["Multi-select", TEST_MULTI_SELECT],
            ["Checkbox", TEST_CHECKBOX],
            ["URL", TEST_URL],
            ["Email", TEST_EMAIL],
            ["Phone", TEST_PHONE],
        ],
    )
    async def test_set_and_get_properties(self, page, property, value):
        await page.set(property, value)
        assert await page.get(property, cache=False) == value

    @mark.parametrize(
        "property,expected_return_value",
        [
            ["Name", ""],
            ["Text", ""],
            ["Number", None],
            ["Select", None],
            ["Multi-select", []],
            ["URL", None],
            ["Email", None],
            ["Phone", None],
        ],
    )
    async def test_set_and_get_properties_empty(
        self, page, property, expected_return_value
    ):
        await page.set(property, None)
        assert await page.get(property, cache=False) == expected_return_value

    async def test_set_date(self, page):
        await page.set("Date", TEST_DATE)
        assert (
            abs(
                (await page.get("Date", cache=False)).start.timestamp()
                - TEST_DATE.timestamp()
            )
            < 60000
        )

    @mark.skip(
        reason="This test will create a notification for the TEST_PEOPLE"
    )
    async def test_set_person(self, page):
        await page.set("Person", TEST_PEOPLE)
        assert await page.get("Person", cache=False) == ["Mihails Delmans"]

    async def test_set_files(self, page):
        await page.set("Files & media", TEST_FILES)
        assert (await page.get("Files & media", cache=False))[
            0
        ].url == TEST_FILES[0].url

    async def test_set_relation(self, page):
        await page.set("Relation", [page.page_id])
        assert (await page.get("Relation", cache=False))[0].replace(
            "-", ""
        ) == page.page_id

    @mark.skip(
        reason="This test will create a notification for the TEST_PEOPLE"
    )
    async def test_create_new_page(self, database):
        new_page = await database.create_page(
            properties={
                "Name": TEST_TITLE,
                "Text": TEST_TEXT,
                "Number": TEST_NUMBER,
                "Select": TEST_SELECT,
                "Multi-select": TEST_MULTI_SELECT,
                "Status": TEST_STATUS,
                "Date": TEST_DATE,
                "Person": TEST_PEOPLE,
                "Files & media": TEST_FILES,
                "Checkbox": TEST_CHECKBOX,
                "URL": TEST_URL,
                "Email": TEST_EMAIL,
                "Phone": TEST_PHONE,
            }
        )
        assert new_page is not None

    async def test_get_unique_id(self, page):
        unique_id = await page.get("Unique ID")
        assert isinstance(unique_id, int)

    async def test_get_by_id(self, page):
        await page.set("Email", TEST_EMAIL)
        email = await page.get("%3E%5Ehh", cache=False)
        assert email == TEST_EMAIL

    async def test_set_by_id(self, page):
        await page.set("%3E%5Ehh", TEST_EMAIL)
        email = await page.get("Email", cache=False)
        assert email == TEST_EMAIL

    async def test_update(self, page):
        await page.update(
            properties={
                "%3E%5Ehh": TEST_EMAIL,
                "Phone": TEST_PHONE,
                "Multi-select": None,
            }
        )

        email = await page.get("Email", cache=False)
        phone = await page.get("Phone", cache=False)
        multi_select = await page.get("Multi-select", cache=False)

        assert email == TEST_EMAIL
        assert phone == TEST_PHONE
        assert not multi_select

    async def test_reload(self, page):
        await page.set("Email", TEST_EMAIL)
        await page.reload()

        email = await page.get("Email", cache=True)
        assert email == TEST_EMAIL


@mark.asyncio
class TestRollups:
    NUMBER_PAGE_ID = "25e800a118414575ab30a8dc42689b74"
    DATE_PAGE_ID = "e38bb90faf8a436895f089fed2446cc6"
    EMPTY_ROLLUP_PAGE_ID = "2b5efae5bad24df884b4f953e3788b64"

    async def test_number_rollup(self, async_api):
        number_page = await async_api.get_page(self.NUMBER_PAGE_ID)
        num = await number_page.get("Number rollup")
        assert num == 10

    async def test_date_rollup(self, async_api):
        date_page = await async_api.get_page(self.DATE_PAGE_ID)
        date = await date_page.get("Date rollup")
        assert isinstance(date.start, datetime)

    async def test_empty_rollup(self, async_api):
        page = await async_api.get_page(self.EMPTY_ROLLUP_PAGE_ID)
        num = await page.get("Number rollup")
        assert num is None


@mark.asyncio
class TestDatabase:
    async def test_query_database(self, database):
        database.query()

    async def test_prop_filter(self, database):
        pages = database.query(
            filters=SelectFilter(property="Select", equals=TEST_SELECT)
        )
        page = await anext(pages)
        value = await page.get("Select")
        assert value == TEST_SELECT

    async def test_and_filter(self, database):
        pages = database.query(
            filters=and_filter(
                [
                    SelectFilter(property="Select", equals=TEST_SELECT),
                    MultiSelectFilter(property="Multi-select", contains="bar"),
                ]
            )
        )
        page = await anext(pages)
        value = await page.get("Select")
        assert value == TEST_SELECT

    async def test_or_filter(self, database):
        pages = database.query(
            filters=or_filter(
                [
                    SelectFilter(property="Select", equals=TEST_SELECT),
                    MultiSelectFilter(property="Multi-select", contains="bar"),
                ]
            )
        )
        page = await anext(pages)
        value = await page.get("Select")
        assert value == TEST_SELECT

    async def test_sort(self, database):
        pages = database.query(sorts=[Sort(property="Date")])
        page = await anext(pages)
        assert page is not None

    async def test_descending_sort(self, database):
        pages = database.query(sorts=[Sort(property="Date", descending=True)])
        page = await anext(pages)
        assert page is not None
