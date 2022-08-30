import os
from notion_integration.api import NotionAPI

from datetime import datetime

TEST_DB = "401076f6c7c04ae796bf3e4c847361e1"

if __name__ == '__main__':
    api = NotionAPI(access_token=os.environ.get("NOTION_SECRET"))

    db = api.get_database(database_id=TEST_DB)
    assert db is not None

    me = api.me()

    new_page = db.create_page(
        properties={
            "Name": f"API Test {datetime.utcnow().isoformat()}",
            "Text": "Test text is boring",
            "Number": 12,
            "Select": "foo",
            "Multi-select": ["foo", "bar", "baz"],
            "Status": "In progress",
            "Date": datetime.now(),
            "Person": "48a7a3d5-95ee-40e7-a6c9-40764201d1a5"
            # "Files & media": "http://example.com/files/2n3j3iek",
            # "Checkbox": True,
            # "URL": "www.colorifix.com",
            # "Email": "admin@colorifix.com",
            # "Phone": "076736529659"
        }
    )

    assert new_page is not None
