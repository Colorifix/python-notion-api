from typing import Literal, Optional, Dict

from datetime import datetime

from pydantic import BaseModel

from notion_integration.api.models.fields import (
    typeField, idField
)


class TextObject(BaseModel):
    content: str
    link: Optional[Dict]


class RichTextObject(BaseModel):
    plain_text: str
    href: Optional[str]
    annotations: Optional[Dict]
    rich_text_type: Literal["text", "mention", "equation"] = typeField
    text: Optional[TextObject]

    @classmethod
    def from_str(cls, plain_text: str):
        text_obj = TextObject(content=plain_text)
        return RichTextObject(
            plain_text=plain_text,
            href=None,
            annotations=dict(),
            type='text',
            text=text_obj
        )


class File(BaseModel):
    name: Optional[str]
    url: str


class ExternalFile(BaseModel):
    url: str


class NotionFile(BaseModel):
    url: str
    expiry_time: str


class FileObject(BaseModel):
    reference_type: str = typeField
    name: Optional[str]
    external: Optional[ExternalFile]
    file: Optional[NotionFile]

    @property
    def value(self):
        if self.external is not None:
            return self.external.url
        elif self.file is not None:
            return self.file.url

    @classmethod
    def from_file(cls, file: File):
        return cls(
            type="external",
            name=file.name,
            external=ExternalFile(url=file.url)
        )

    @classmethod
    def from_url(cls, url: str):
        return cls(
            type="external",
            external=ExternalFile(url=url)
        )


class EmojiObject(BaseModel):
    emoji_type: Literal["emoji"] = typeField
    emoji: str


class ParentObject(BaseModel):
    parent_type: str = typeField
    page_id: Optional[str]
    database_id: Optional[str]


class SelectObject(BaseModel):
    select_id: Optional[str] = idField
    name: str
    color: Optional[str]


class StatusObject(BaseModel):
    status_id: Optional[str] = idField
    name: str
    color: Optional[str]


class DateObject(BaseModel):
    start: datetime
    end: Optional[datetime]
    time_zone: Optional[str]


class RelationObject(BaseModel):
    relation_id: str = idField
