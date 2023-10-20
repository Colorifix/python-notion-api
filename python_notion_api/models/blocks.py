from __future__ import annotations
from typing import List, Optional, Union, Dict
from pydantic import BaseModel, AnyUrl
from python_notion_api.models.common import (
    RichTextObject, FileObject, EmojiObject
)
from python_notion_api.models.objects import Block
from python_notion_api.models.fields import typeField


class RCCBlockValue(BaseModel):
    # rich_text, color, children combination used by many classes.
    rich_text: List[RichTextObject]
    color: Optional[str]
    children: Optional[List[Block]]


class ParagraphBlockValue(RCCBlockValue):
    pass


class QuoteBlockValue(RCCBlockValue):
    pass


class BulletedListItemBlockValue(RCCBlockValue):
    pass


class NumberedListItemBlockValue(RCCBlockValue):
    pass


class ToggleBlockValue(RCCBlockValue):
    pass


class HeadingBlockValue(BaseModel):
    rich_text: List[RichTextObject]
    color: Optional[str]
    is_toggleable: bool


class CalloutBlockValue(BaseModel):
    rich_text: List[RichTextObject]
    icon: Union[FileObject, EmojiObject]
    color: Optional[str]
    children: Optional[List[Block]]


class ToDoBlockValue(BaseModel):
    rich_text: List[RichTextObject]
    checked: bool
    color: Optional[str]
    children: Optional[List[Block]]


class CodeBlockValue(BaseModel):
    rich_text: List[RichTextObject]
    caption: List[RichTextObject]
    language: str


class ChildPageBlockValue(BaseModel):
    title: str


class ChildDatabaseBlockValue(BaseModel):
    title: str


class EmbedBlockValue(BaseModel):
    url: AnyUrl


class ImageBlockValue(BaseModel):
    image: FileObject


class VideoBlockValue(BaseModel):
    video: FileObject


class FileBlockValue(BaseModel):
    file: FileObject
    caption: List[RichTextObject]


class PDFBlockValue(BaseModel):
    pdf: FileObject


class BookmarkBlockValue(BaseModel):
    url: str
    caption: List[RichTextObject]


class EquationBlockValue(BaseModel):
    expression: str


class TableOfContentsBlockValue(BaseModel):
    color: Optional[str]


class ColumnListBlockValue(BaseModel):
    children: List[ColumnBlock]


class ColumnBlockValue(BaseModel):
    children: List[Block]


class LinkPreviewBlockValue(BaseModel):
    url: str


class TemplateBlockValue(BaseModel):
    rich_text: List[RichTextObject]
    children: List[Block]


class LinkToPageBlockValue(BaseModel):
    link_type: str = typeField
    page_id: str
    database_id: str


class BlockID(BaseModel):
    block_id: str


class SyncedBlockValue(BaseModel):
    synced_from: Optional[BlockID]
    children: List[Block]


class TableBlockValue(BaseModel):
    table_width: int
    has_column_header: bool
    has_row_header: bool
    children: List[TableRowBlock]


class TableRowBlockValue(BaseModel):
    cells: List[RichTextObject]


class ParagraphBlock(Block):
    _class_key_field = None

    paragraph: ParagraphBlockValue


class Heading1Block(Block):
    _class_key_field = None

    heading_1: HeadingBlockValue


class Heading2Block(Block):
    _class_key_field = None

    heading_2: HeadingBlockValue


class Heading3Block(Block):
    _class_key_field = None

    heading_3: HeadingBlockValue


class CalloutBlock(Block):
    _class_key_field = None

    callout: CalloutBlockValue


class QuoteBlock(Block):
    _class_key_field = None

    quote: QuoteBlockValue


class BulletedListItemBlock(Block):
    _class_key_field = None

    bulleted_list_item: BulletedListItemBlockValue


class NumberedListItemBlock(Block):
    _class_key_field = None

    numbered_list_item: NumberedListItemBlockValue


class ToDoBlock(Block):
    _class_key_field = None

    to_do: ToDoBlockValue


class CodeBlock(Block):
    _class_key_field = None

    code: CodeBlockValue


class ChildPageBlock(Block):
    _class_key_field = None

    child_page: ChildPageBlockValue


class ChildDatabaseBlock(Block):
    _class_key_field = None

    child_database: ChildDatabaseBlockValue


class EmbedBlock(Block):
    _class_key_field = None

    embed: EmbedBlockValue


class ImageBlock(Block):
    _class_key_field = None

    image: ImageBlockValue


class VideoBlock(Block):
    _class_key_field = None

    video: VideoBlockValue


class FileBlock(Block):
    _class_key_field = None

    file: FileBlockValue


class PDFBlock(Block):
    _class_key_field = None

    pdf: PDFBlockValue


class BookmarkBlock(Block):
    _class_key_field = None

    bookmark: BookmarkBlockValue


class EquationBlock(Block):
    _class_key_field = None

    equation: EquationBlockValue


class DividerBlock(Block):
    _class_key_field = None
    # There is no information in a DividerBlock


class TableOfContentsBlock(Block):
    _class_key_field = None

    table_of_contents: TableOfContentsBlockValue


class BreadcrumbBlock(Block):
    _class_key_field = None
    # There is no information in a BreadcrumbBlock


class ColumnListBlock(Block):
    _class_key_field = None

    column_list: ColumnListBlockValue


class ColumnBlock(Block):
    _class_key_field = None

    column: ColumnBlockValue


class LinkPreviewBlock(Block):
    _class_key_field = None

    link_preview: LinkPreviewBlockValue


class TemplateBlock(Block):
    _class_key_field = None

    template: TemplateBlockValue


class LinkToPageBlock(Block):
    _class_key_field = None

    link_to_page: LinkToPageBlockValue


class SyncedBlock(Block):
    _class_key_field = None

    synced: SyncedBlockValue


class TableBlock(Block):
    _class_key_field = None

    table: TableBlockValue


class TableRowBlock(Block):
    _class_key_field = None

    table_row: TableRowBlockValue


class UnsupportedBlock(Block):
    _class_key_field = None

    unsupported: dict
