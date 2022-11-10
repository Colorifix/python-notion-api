
from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, root_validator, ValidationError, AnyUrl
from python_notion_api.models.common import RichTextObject
from python_notion_api.models.objects import Block


class ParagraphBlockValue(BaseModel):
    rich_text: List[RichTextObject]
    color: Optional[str]
    children: Optional[List[Block]]


class EmbedBlockValue(BaseModel):
    url: AnyUrl


class ParagraphBlock(Block):
    _class_key_field = None

    paragraph: ParagraphBlockValue

    @root_validator(pre=True)
    def validate_block(cls, values):
        try:
            obj = ParagraphBlockValue(**values)
            return {
                "paragraph": obj,
                "object": "block",
                "type": "paragraph"
            }
        except ValidationError:
            pass
        return values


class EmbedBlock(Block):
    _class_key_field = None

    embed: EmbedBlockValue

    @root_validator(pre=True)
    def validate_block(cls, values):
        try:
            obj = EmbedBlockValue(**values)
            return {
                "embed": obj,
                "object": "block",
                "type": "embed"
            }
        except ValidationError:
            pass
        return values
