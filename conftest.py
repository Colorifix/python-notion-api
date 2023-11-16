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
    return "e439b7a7296d45b98805f24c9cfc2115"


@fixture
def example_page_id_2() -> str:
    return "d5bce0a0fe6248d0a120c6c693d9b597"
