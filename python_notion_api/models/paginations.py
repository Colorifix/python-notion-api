from typing import Dict, List, Union

from python_notion_api.models.objects import (
    Block,
    DataSource,
    Page,
    Pagination,
)
from python_notion_api.models.properties import PropertyItem


class PagePagination(Pagination):
    _class_key_field = None

    page: Dict
    results: List[Page]


class PageOrDataSourcePagination(Pagination):
    _class_key_field = None

    page_or_data_source: Dict
    results: List[Union[Page, DataSource]]


class PropertyItemPagination(Pagination):
    _class_key_field = None

    property_item: Dict
    results: List[PropertyItem]


class BlockPagination(Pagination):
    _class_key_field = None

    block: Dict
    results: List[Block]
