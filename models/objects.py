from pydantic import BaseModel, Field, Extra
from typing import Literal, Optional, Dict, List, Union, ClassVar

from datetime import datetime

from notion_integration.api.models.fields import (
    idField, typeField, objectField
)


def get_derived_class(base_class, derived_cass_name):
    return next((
        cls for cls in base_class.__subclasses__()
        if cls.__name__ == derived_cass_name
    ), None)


class NotionObjectBase(BaseModel):
    _class_map: ClassVar[Dict[str, str]]

    @classmethod
    def from_obj(cls, obj):
        temp_obj = cls(**obj)

        class_key_value = temp_obj._class_key_field
        if class_key_value is None:
            return temp_obj

        class_name = cls._class_map.get(class_key_value, None)
        if class_name is None:
            raise ValueError(
                f"Unknown object"
                f"{temp_obj._class_key_field}: '{class_key_value}'"
            )
        derived_cls = get_derived_class(cls, class_name)

        if derived_cls is None:
            raise ValueError(f"Can find {class_name}({cls.__name__})")

        return derived_cls.from_obj(obj)

    @property
    def _class_key_field(self):
        return None


class NotionObject(NotionObjectBase, extra=Extra.allow):
    notion_object: str = objectField

    _class_map = {
        "list": "Pagination",
        "property_item": "PropetyItem",
        "database": "Database",
        "page": "Page"
    }

    @property
    def _class_key_field(self):
        return self.notion_object


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


class RichTextObject(BaseModel):
    plain_text: str
    href: Optional[str]
    annotations: Dict
    rich_text_type: Literal["text", "mention", "equation"] = typeField


class FileObject(BaseModel):
    url: str


class FileReferenceObject(BaseModel):
    reference_type: str = typeField
    name: str
    external: Optional[FileObject]
    file: Optional[FileObject]

    @property
    def value(self):
        if self.external is not None:
            return self.external.url
        elif self.file is not None:
            return self.file.url


class EmojiObject(BaseModel):
    emoji_type: Literal["emoji"] = typeField
    emoji: str


class UserObject(BaseModel):
    user_object: Literal["user"] = objectField
    user_id: str = idField
    user_type: Optional[Literal["person", "bot"]] = typeField
    name: Optional[str]
    avatar_url: Optional[str]
    person: Optional[Dict]
    person_email: Optional[str] = Field(alias="person.email")
    bot: Optional[Dict]
    owner_type: Optional[
        Literal["workspace", "user"]
    ] = Field(alias="owner.type")


class Database(NotionObject):
    _class_key_field = None

    db_object: str = objectField
    db_id: str = idField
    created_time: str
    created_by: UserObject
    last_edited_time: str
    last_edited_by: UserObject
    title: List[RichTextObject]
    description: List[RichTextObject]
    icon: Optional[Union[FileObject, EmojiObject]]
    cover: Optional[FileObject]
    properties: Dict
    parent: Dict
    url: str
    archived: bool
    is_inline: bool


class ParentObject(BaseModel):
    parent_type: str = typeField
    page_id: Optional[str]
    database_id: Optional[str]


class PropertyObject(BaseModel):
    property_id: str = idField


class Page(NotionObject):
    _class_key_field = None

    page_object: str = objectField
    page_id: str = idField
    created_time: datetime
    created_by: UserObject
    last_edited_time: datetime
    last_edited_by: UserObject
    cover: Optional[FileObject]
    properties: Dict[str, PropertyObject]
    parent: ParentObject


class PagePagination(Pagination):
    _class_key_field = None

    page: Dict
    results: List[Page]


class DatePropertyValueObject(BaseModel):
    start: datetime
    end: Optional[datetime]
    time_zone: Optional[str]


class SelectObject(BaseModel):
    select_id: str = idField
    name: str
    color: str


class StatusObject(BaseModel):
    status_id: str = idField
    name: str
    color: str


class FormulaObject(BaseModel):
    formula_type: str = typeField


class FormulaConfigurationObject(BaseModel):
    expression: str


class PageReferenceObject(BaseModel):
    page_id: str = idField


class RollupObject(BaseModel):
    rollup_type: str = typeField


class RelationConfigurationObject(BaseModel):
    database_id: str
    synced_property_name: Optional[str]
    synced_property_id: Optional[str]


class RollupConfigurationObject(BaseModel):
    relation_property_name: str
    relation_property_id: str
    rollup_property_name: str
    rollup_property_id: str
    function: str 
