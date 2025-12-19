import os

from pytest import fixture

from python_notion_api.async_api.api import AsyncNotionAPI


@fixture
def async_api() -> AsyncNotionAPI:
    return AsyncNotionAPI(access_token=os.environ["NOTION_TOKEN"])


@fixture
def cover_url() -> str:
    return (
        "https://images.unsplash.com/"
        "photo-1514888286974-6c03e2ca1dba?ixlib=rb-1.2.1&"
        "ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8"
        "&auto=format&fit=crop&w=2286&q=80"
    )


@fixture
def example_page_id() -> str:
    return "2cef2075b1dc803a8ec3d142ac105817"


@fixture(scope="session")
def database_id() -> str:
    return "2cef2075b1dc8023b0ece0dbf9b278f7"


@fixture(scope="session")
def data_source_id1() ->  str:
    return "2cef2075b1dc80bab834000b42b068d7"


@fixture
def data_source_id2() -> str:
    return "2cef2075b1dc80048d8d000b1b75df8f"


@fixture
def block_id() -> str:
    return "2cef2075b1dc80a59d6ad9ed97846ff8"