from pydantic import BaseModel, Field, Extra
from typing import Literal, Optional, Dict, List, Union, ClassVar

from datetime import datetime

from notion_integration.api.models.fields import (
    idField, typeField, objectField
)

from notion_integration.api.models.common import (
    RichTextObject,
    EmojiObject,
    FileObject,
    ParentObject
)

from notion_integration.api.utils import get_derived_class


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
            if class_key_value == 'rollup':
                return None  # Not implemented
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
        "user": "User"
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
        "page": "PagePagination"
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


class PropertyObject(BaseModel):
    property_id: str = idField


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
    properties: Dict[str, PropertyObject]
    parent: ParentObject
