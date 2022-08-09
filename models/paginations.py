from typing import Dict, List

from notion_integration.api.models.objects import Pagination, Page


class PagePagination(Pagination):
    _class_key_field = None

    page: Dict
    results: List[Page]


class PropertyItemPagination(Pagination):
    property_item: Dict

    _class_map = {
        "rich_text": "RichTextPagination",
        "title": "TitlePagination",
        "people": "PeoplePagination",
        "relation": "RelationPagination",
        "rollup": "RollupPagination"
    }

    @property
    def _class_key_field(self):
        return self.property_item['type']

    @classmethod
    def create_new(cls, value):
        """Creates a new property item with the given value.
        Not all fields may be correctly filled to match pydantic's requirements
        For creating new items to be posted.

        """
        obj = cls.construct()
        obj.set_value(value)
        return obj
