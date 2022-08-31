import os

from typing import Union, Optional

from notion_integration.api import NotionAPI
from pydantic import BaseModel, root_validator, validator

from datetime import datetime


class TestModel(BaseModel):
    init: Union[int, bool]
    foo: str

    @root_validator(pre=True)
    def check_foo(cls, values):
        init = values['init']
        if isinstance(init, bool):
            values['foo'] = cls._from_bool(init)
        elif isinstance(init, int):
            values['foo'] = cls._from_bool(init)
        return values

    @staticmethod
    def _from_int(init: int):
        return str(init)

    @staticmethod
    def _from_bool(init: bool):
        return str(init)


TEST_DB = "401076f6c7c04ae796bf3e4c847361e1"

if __name__ == '__main__':
    api = NotionAPI(access_token=os.environ.get("NOTION_SECRET"))

    db = api.get_database(database_id=TEST_DB)
    assert db is not None

    me = api.me()

    new_page = db.create_page(
        properties={
            # "Name": f"API Test {datetime.utcnow().isoformat()}",
            # "Text": "Test text is boring",
            # "Number": 12,
            # "Select": "foo",
            # "Multi-select": ["foo", "bar", "baz"],
            # "Status": "In progress",
            # "Date": datetime.now(),
            # "Person": "48a7a3d5-95ee-40e7-a6c9-40764201d1a5"
            # "Files & media": "http://example.com/files/2n3j3iek",
            # "Checkbox": True,
            # "URL": "www.colorifix.com",
            # "Email": "admin@colorifix.com",
            # "Phone": "076736529659"
        }
    )

    assert new_page is not None

    timestamp = f"API Test {datetime.utcnow().isoformat()}"

    new_page.set("Name", timestamp)
    assert new_page.get("Name").value == timestamp

    test_text = "Test text is boring"
    new_page.set("Text", test_text)

    assert new_page.get("Text").value == test_text

    test_number = 12.5
    new_page.set("Number", test_number)

    assert new_page.get("Number").value == test_number

    test_select = "foo"
    new_page.set("Select", test_select)

    assert new_page.get("Select").value == test_select

    test_status = "In progress"
    new_page.set("Status", test_status)

    assert new_page.get("Status").value == test_status

    test_multi_select = ["foo", "bar", "baz"]
    new_page.set("Multi-select", test_multi_select)

    assert new_page.get("Multi-select").value == test_multi_select