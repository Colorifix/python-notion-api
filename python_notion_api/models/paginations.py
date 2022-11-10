from typing import Dict, List

from python_notion_api.models.objects import Pagination, Page, Block
from python_notion_api.models.properties import PropertyItem


class PagePagination(Pagination):
    _class_key_field = None

    page: Dict
    results: List[Page]


class PropertyItemPagination(Pagination):
    _class_key_field = None

    property_item: Dict
    results: List[PropertyItem]


class BlockPagination(Pagination):
    _class_key_field = None

    block: Dict
    results: List[Block]
