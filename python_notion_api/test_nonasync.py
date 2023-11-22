import os
from datetime import datetime

from pytest import fixture, mark

from python_notion_api import File, NotionAPI
from python_notion_api.models.filters import (
    MultiSelectFilter,
    NumberFilter,
    SelectFilter,
    and_filter,
    or_filter,
)
from python_notion_api.models.sorts import Sort

TEST_DB = "401076f6c7c04ae796bf3e4c847361e1"

TEST_TITLE = f"API Test {datetime.utcnow().isoformat()}"
TEST_TEXT = "Test text is boring"
TEST_NUMBER = 12.5
TEST_SELECT = "foo"
TEST_STATUS = "In progress"
TEST_MULTI_SELECT = ["foo", "bar", "baz"]
TEST_DATE = datetime.now()
TEST_PEOPLE = ["fa9e1df9-7c24-427c-9c20-eac629565fe4"]
TEST_FILES = [File(name="foo.pdf", url="http://example.com/file")]
TEST_CHECKBOX = True
TEST_URL = "http://colorifix.com"
TEST_EMAIL = "admin@colorifix.com"
TEST_PHONE = "079847364088"


@fixture
def api():
    return NotionAPI(access_token=os.environ.get("NOTION_TOKEN"))


@fixture
def database(api):
    return api.get_database(database_id=TEST_DB)


class TestCore:
    def test_database_id(self, database):
        assert database.database_id == TEST_DB

    def test_create_empty_page(self, database):
        new_page = database.create_page()
        assert new_page is not None

    def test_create_empty_page_with_cover(self, database, cover_url):
        new_page = database.create_page(cover_url=cover_url)
        assert new_page is not None

    def test_get_page(self, api, example_page_id):
        page = api.get_page(page_id=example_page_id)
        assert isinstance(page.to_dict(), dict)


class TestPage:
    @fixture(scope="class")
    def api(cls):
        return NotionAPI(access_token=os.environ.get("NOTION_TOKEN"))

    @fixture(scope="class")
    def database(cls, api):
        return api.get_database(database_id=TEST_DB)

    @fixture(scope="class")
    def new_page(cls, database):
        return database.create_page()

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
    def test_set_and_get_properties(self, new_page, property, value):
        new_page.set(property, value)
        assert new_page.get(property, cache=False).value == value

    def test_set_date(self, new_page):
        new_page.set("Date", TEST_DATE)
        assert (
            abs(
                new_page.get("Date", cache=False).value.start.timestamp()
                - TEST_DATE.timestamp()
            )
            < 60000
        )

    @mark.skip(
        reason="This test will create a notification for the TEST_PEOPLE"
    )
    def test_set_person(self, new_page):
        new_page.set("Person", TEST_PEOPLE)
        assert new_page.get("Person", cache=False).value == ["Mihails Delmans"]

    def test_set_files(self, new_page):
        new_page.set("Files & media", TEST_FILES)
        assert (
            new_page.get("Files & media", cache=False).value[0].url
            == TEST_FILES[0].url
        )

    def test_set_relation(self, new_page):
        new_page.set("Relation", [new_page.page_id])
        assert (
            new_page.get("Relation", cache=False).value[0].replace("-", "")
            == new_page.page_id
        )

    def test_set_alive(self, new_page):
        new_page.alive = False
        assert not new_page.alive
        new_page.alive = True
        assert new_page.alive

    @mark.skip(
        reason="This test will create a notification for the TEST_PEOPLE"
    )
    def test_create_new_page(self, database):
        new_page = database.create_page(
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

    def test_get_unique_id(self, new_page):
        unique_id = new_page.get("Unique ID").value
        assert isinstance(unique_id, int)

    def test_get_by_id(self, new_page):
        new_page.set("Email", TEST_EMAIL)
        email = new_page.get("%3E%5Ehh", cache=False).value
        assert email == TEST_EMAIL

    def test_set_by_id(self, new_page):
        new_page.set("%3E%5Ehh", TEST_EMAIL)
        email = new_page.get("Email", cache=False).value
        assert email == TEST_EMAIL

    def test_update(self, new_page):
        new_page.update(
            properties={"%3E%5Ehh": TEST_EMAIL, "Phone": TEST_PHONE}
        )

        email = new_page.get("Email", cache=False).value
        phone = new_page.get("Phone", cache=False).value

        assert email == TEST_EMAIL
        assert phone == TEST_PHONE

    def test_reload(self, new_page):
        new_page.set("Email", TEST_EMAIL)
        new_page.reload()
        email = new_page.get("Email", cache=True).value
        assert email == TEST_EMAIL


class TestRollups:
    NUMBER_PAGE_ID = "25e800a118414575ab30a8dc42689b74"
    DATE_PAGE_ID = "e38bb90faf8a436895f089fed2446cc6"
    EMPTY_ROLLUP_PAGE_ID = "2b5efae5bad24df884b4f953e3788b64"

    def test_number_rollup(self, api):
        number_page = api.get_page(self.NUMBER_PAGE_ID)
        num = number_page.get("Number rollup")
        assert num.value == 10

    def test_date_rollup(self, api):
        date_page = api.get_page(self.DATE_PAGE_ID)
        date = date_page.get("Date rollup")
        assert isinstance(date.value.start, datetime)

    def test_empty_rollup(self, api):
        page = api.get_page(self.EMPTY_ROLLUP_PAGE_ID)
        num = page.get("Number rollup")
        assert num.value is None


class TestDatabase:
    @fixture(scope="class")
    def api(cls):
        return NotionAPI(access_token=os.environ.get("NOTION_TOKEN"))

    @fixture(scope="class")
    def database(cls, api):
        return api.get_database(database_id=TEST_DB)

    def test_query_database(self, database):
        database.query()

    def test_prop_filter(self, database):
        pages = database.query(
            filters=SelectFilter(property="Select", equals=TEST_SELECT)
        )
        page = next(pages)
        assert page.get("Select").value == TEST_SELECT

    def test_and_filter(self, database):
        pages = database.query(
            filters=and_filter(
                [
                    SelectFilter(property="Select", equals=TEST_SELECT),
                    MultiSelectFilter(property="Multi-select", contains="bar"),
                ]
            )
        )
        page = next(pages)
        assert page.get("Select").value == TEST_SELECT

    def test_large_and_filter(self, database):
        pages = database.query(
            filters=and_filter(
                [NumberFilter(property="Number", equals=TEST_NUMBER)]
                + [
                    NumberFilter(property="Number", less_than=x)
                    for x in range(
                        int(TEST_NUMBER + 2), int(TEST_NUMBER + 110)
                    )
                ]
            )
        )
        page = next(pages)
        assert page.get("Number").value == TEST_NUMBER

    def test_or_filter(self, database):
        pages = database.query(
            filters=or_filter(
                [
                    SelectFilter(property="Select", equals=TEST_SELECT),
                    MultiSelectFilter(property="Multi-select", contains="bar"),
                ]
            )
        )
        page = next(pages)
        assert page.get("Select").value == TEST_SELECT

    def test_large_or_filter(self, database):
        pages = database.query(
            filters=or_filter(
                [
                    SelectFilter(property="Select", equals=TEST_SELECT),
                ]
                + [
                    SelectFilter(property="Select", equals=str(x))
                    for x in range(110)
                ]
            )
        )
        page = next(pages)
        assert page.get("Select").value == TEST_SELECT

    def test_sort(self, database):
        pages = database.query(sorts=[Sort(property="Date")])
        page = next(pages)
        assert page is not None

    def test_descending_sort(self, database):
        pages = database.query(sorts=[Sort(property="Date", descending=True)])
        page = next(pages)
        assert page is not None


@mark.parametrize(
    "filter_type,filter_attribute",
    [[or_filter, "filter_or"], [and_filter, "filter_and"]],
)
@mark.parametrize(
    "full_length,num_splits,split_lengths",
    [[199, 2, [100, 99]], [200, 2, [100, 100]], [201, 3, [100, 100, 1]]],
)
def test_large_filter_lengths(
    filter_type, filter_attribute, full_length, num_splits, split_lengths
):
    filters = filter_type(
        [NumberFilter(property="Number", equals=x) for x in range(full_length)]
    )
    assert len(getattr(filters, filter_attribute)) == num_splits
    for i, split in enumerate(getattr(filters, filter_attribute)):
        assert len(getattr(split, filter_attribute)) == split_lengths[i]
