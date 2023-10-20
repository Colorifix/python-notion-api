from pydantic import BaseModel, Field, Extra, root_validator, ValidationError
from typing import Literal, Optional, Dict, List, Union, ClassVar, Type

from datetime import datetime

from python_notion_api.models.fields import (
    idField, typeField, objectField
)

from python_notion_api.models.common import (
    RichTextObject,
    EmojiObject,
    FileObject,
    ParentObject
)

from python_notion_api.utils import get_derived_class


class NotionObjectBase(BaseModel):
    _class_map: ClassVar[Dict[str, str]]

    @classmethod
    def from_obj(cls, obj):
        try:
            temp_obj = cls(**obj)
        except Exception as e:
            raise Exception(
                f"Failed to create {cls} object from {obj}"
            ) from e

        class_key_value = temp_obj._class_key_field
        if class_key_value is None:
            return temp_obj

        class_name = cls._class_map.get(class_key_value, None)
        if class_name is None:
            raise ValueError(
                f"Unknown object\n"
                f"{temp_obj._class_key_field}: '{class_key_value}'"
            )

        derived_cls = get_derived_class(cls, class_name)

        if derived_cls is None:
            raise ValueError(f"Cannot find {class_name}({cls.__name__})")

        return derived_cls.from_obj(obj)

    @property
    def _class_key_field(self):
        return None


class NotionObject(NotionObjectBase, extra=Extra.allow):
    notion_object: str = objectField

    _class_map = {
        "list": "Pagination",
        "property_item": "PropertyItem",
        "database": "Database",
        "page": "Page",
        "user": "User",
        "block": "Block"
    }

    @property
    def _class_key_field(self):
        return self.notion_object


class User(NotionObject):
    _class_key_field = None

    user_id: Optional[str] = idField
    user_type: Optional[Literal["person", "bot"]] = typeField
    name: Optional[str]
    avatar_url: Optional[str]
    person: Optional[Dict]
    person_email: Optional[str] = Field(alias="person.email")
    bot: Optional[Dict]
    owner_type: Optional[
        Literal["workspace", "user"]
    ] = Field(alias="owner.type")

    @classmethod
    def from_id(cls, id: str):
        return cls(
            object="user",
            id=id
        )

    @classmethod
    def from_name(cls, name: str):
        return cls(
            object="user",
            name=name
        )


class Pagination(NotionObject):
    has_more: bool
    next_cursor: Optional[str]
    results: List
    pagination_type: Literal[
        "block", "page", "user", "database", "property_item",
        "page_or_database"
    ] = typeField

    _class_map = {
        "property_item": "PropertyItemPagination",
        "page": "PagePagination",
        "block": "BlockPagination",
        "page_or_database": "PageOrDatabasePagination",
    }

    @property
    def _class_key_field(self):
        return self.pagination_type


class Database(NotionObject):
    _class_key_field = None

    db_object: str = objectField
    db_id: str = idField
    created_time: str
    created_by: User
    last_edited_time: str
    last_edited_by: User
    title: List[RichTextObject]
    description: List[RichTextObject]
    icon: Optional[Union[FileObject, EmojiObject]]
    cover: Optional[Union[FileObject,
                          Dict[str, Union[str, FileObject]]]]
    properties: Dict
    parent: Dict
    url: str
    archived: bool
    is_inline: bool


class Page(NotionObject):
    _class_key_field = None

    page_object: str = objectField
    page_id: str = idField
    created_time: datetime
    created_by: User
    last_edited_time: datetime
    last_edited_by: User
    cover: Optional[Union[FileObject,
                          Dict[str, Union[str, FileObject]]]]
    properties: Dict[str, Dict]
    parent: ParentObject


class Block(NotionObject):
    block_type: Literal[
        "paragraph", "heading_1", "heading_2", "heading_3", "callout",
        "quote", "bulleted_list_item", "numbered_list_item", "to_do", "toggle",
        "code", "child_page", "child_database", "embed", "image", "video",
        "file", "pdf", "bookmark", "equation", "divider", "table_of_contents",
        "breadcrumb", "column_list", "column", "link_preview", "template",
        "link_to_page", "synced_block", "table", "table_row", "unsupported"
    ] = typeField

    _class_map = {
        "paragraph": "ParagraphBlock",
        "heading_1": "Heading1Block",
        "heading_2": "Heading2Block",
        "heading_3": "Heading3Block",
        "callout": "CalloutBlock",
        "quote": "QuoteBlock",
        "bulleted_list_item": "BulletedListItemBlock",
        "numbered_list_item": "NumberedListItemBlock",
        "to_do": "ToDoBlock",
        "toggle": "ToggleBlock",
        "code": "CodeBlock",
        "child_page": "ChildPageBlock",
        "child_database": "ChildDatabaseBlock",
        "embed": "EmbedBlock",
        "image": "ImageBlock",
        "video": "VideoBlock",
        "file": "FileBlock",
        "pdf": "PDFBlock",
        "bookmark": "BookmarkBlock",
        "equation": "EquationBlock",
        "divider": "DividerBlock",
        "table_of_contents": "TableOfContentsBlock",
        "breadcrumb": "BreadcrumbBlock",
        "column_list": "ColumnListBlock",
        "column": "ColumnBlock",
        "link_preview": "LinkPreviewBlock",
        "template": "TemplateBlock",
        "link_to_page": "LinkToPageBlock",
        "synced_block": "SyncedBlock",
        "table": "TableBlock",
        "table_row": "TableRowBlock",
        "unsupported": "UnsupportedBlock"
    }
    _block_map = {v: k for k, v in _class_map.items()}

    id: Optional[str] = idField
    parent: Optional[ParentObject]
    created_time: Optional[datetime]
    last_edited_time: Optional[datetime]
    created_by: Optional[User]
    last_edited_by: Optional[User]
    has_children: Optional[bool]
    archived: Optional[bool]

    @property
    def _class_key_field(self):
        return self.block_type

    @root_validator(pre=True)
    def validate_block(cls, values):
        try:
            block_type = cls._block_map.get(cls.__name__, None)
            if block_type is None:
                # It is a Block, not a subclass
                return values
            else:
                try:
                    value_type = cls.__fields__[block_type].type_
                except KeyError as e:
                    # One of the blocks with no stored information
                    return {
                        "object": "block",
                        "type": block_type
                    }

                obj = value_type(**values)
                return {
                    block_type: obj,
                    "object": "block",
                    "type": block_type
                }
        except ValidationError:
            pass
        return values
