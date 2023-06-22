from datetime import date, datetime
from io import BytesIO
import os
from typing import Dict, List, Literal, Optional, Union

from python_notion_api.models.fields import idField, typeField
from python_notion_api.gdrive import GDrive
from pydantic import BaseModel


class LinkObject(BaseModel):
    link_type: Optional[Literal['url']] = typeField
    url: str


class TextObject(BaseModel):
    content: str
    link: Optional[LinkObject]


class File(BaseModel):
    name: Optional[str]
    url: str

    @classmethod
    def from_file_path(
        cls,
        file_path: str,
        parent_id: str,
        overwrite: bool = False
    ):
        gdrive = GDrive()
        file = gdrive.add_media(
            file=file_path,
            parent_id=parent_id,
            file_name=os.path.basename(file_path),
            overwrite=overwrite
        )
        return cls(
            name=file.get("title"),
            url=file.get("alternateLink")
        )

    @classmethod
    def from_stream(
        cls,
        stream: BytesIO,
        parent_id: str,
        file_name: str,
        format: str,
        overwrite: bool = False
    ):
        gdrive = GDrive()
        file = gdrive.add_media(
            file=stream,
            parent_id=parent_id,
            file_name=file_name,
            format=format,
            overwrite=overwrite
        )
        return cls(
            name=file.get("title"),
            url=file.get("alternateLink")
        )


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

    @classmethod
    def from_file(cls, file=File):
        text_obj = TextObject(
            content=file.name,
            link=LinkObject(type='url', url=file.url)
        )
        return RichTextObject(
            plain_text=text_obj.content,
            type='text',
            text=text_obj
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
    start: Union[datetime, date]
    end: Optional[Union[datetime, date]]
    time_zone: Optional[str]


class RelationObject(BaseModel):
    relation_id: str = idField


class FormulaObject(BaseModel):
    formula_type: str = typeField
    string: Optional[str]
    number: Optional[float]
    date: Optional[Union[datetime, date, DateObject]]
    boolean: Optional[bool]


class RollupObject(BaseModel):
    rollup_type: str = typeField
    function: str
    array: Optional[List]
    number: Optional[float]
    date: Optional[DateObject]


class UniqueIDObject(BaseModel):
    prefix: Optional[str]
    number: int
