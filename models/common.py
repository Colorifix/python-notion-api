from typing import Literal, Optional, Dict

from pydantic import BaseModel

from notion_integration.api.models.fields import (
    typeField
)


class RichTextObject(BaseModel):
    plain_text: str
    href: Optional[str]
    annotations: Dict
    rich_text_type: Literal["text", "mention", "equation"] = typeField


class FileObject(BaseModel):
    url: str


class EmojiObject(BaseModel):
    emoji_type: Literal["emoji"] = typeField
    emoji: str


class ParentObject(BaseModel):
    parent_type: str = typeField
    page_id: Optional[str]
    database_id: Optional[str]
