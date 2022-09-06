from typing import Dict, List

from notion_integration.api.models.objects import Pagination, Page
from notion_integration.api.models.properties import PropertyItem


class PagePagination(Pagination):
    _class_key_field = None

    page: Dict
    results: List[Page]


class PropertyItemPagination(Pagination):
    _class_key_field = None

    property_item: Dict
    results: List[PropertyItem]

