from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, List, Union
from datetime import datetime

from notion_integration.api.models.fields import (
    idField, typeField, objectField
)


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


class DatabaseObject(BaseModel):
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


class DatePropertyValueObject(BaseModel):
    start: str
    end: Optional[str]
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
