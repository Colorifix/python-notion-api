from typing import Union, Optional, List, ClassVar, Dict, Type

from datetime import datetime, date

from pydantic import BaseModel, root_validator

from notion_integration.api.models.fields import (
    idField,
    typeField
)

from notion_integration.api.models.common import (
    FileObject, RichTextObject
)


class PropertyValue(BaseModel):
    _type_map: ClassVar
    _set_field: ClassVar[str]

    @root_validator(pre=True)
    def vaidate_init(cls, values):
        init = values.get('init', None)
        for check_type, method_name in cls._type_map.items():
            if isinstance(init, check_type):
                values[cls._set_field] = getattr(cls, method_name)(init)
                break
        return values

    @classmethod
    def leave_unchanged(cls, init):
        return init


class TitlePropertyValue(PropertyValue):
    _type_map = {
        str: 'validate_str',
        List[RichTextObject]: 'leave_unchanged',
        RichTextObject: 'validate_rich_test'
    }
    _set_field = 'title'

    init: Optional[Union[RichTextObject, str, List[RichTextObject]]]
    title: List[RichTextObject]

    @classmethod
    def validate_str(cls, init: str):
        return [RichTextObject.from_str(init)]

    @classmethod
    def validate_rich_text(cls, init: RichTextObject):
        return [init]


class RichTextPropertyValue(PropertyValue):
    _type_map = {
        str: 'validate_str',
        List: 'leave_unchanged',
        RichTextObject: 'validate_rich_test'
    }
    _set_field = 'rich_text'

    init: Optional[Union[RichTextObject, str, List[RichTextObject]]]
    rich_text: List[RichTextObject]

    @classmethod
    def validate_str(cls, init: str):
        return [RichTextObject.from_str(init)]

    @classmethod
    def validate_rich_text(cls, init: RichTextObject):
        return [init]


class NumberPropertyValue(PropertyValue):
    _type_map = {
        float: 'leave_unchanged',
        int: 'leave_unchanged',
    }
    _set_field = 'number'

    init: Optional[Union[float, int]]
    number: float


class SelectValue(BaseModel):
    select_id: Optional[str] = idField
    name: str
    color: Optional[str]


class SelectPropertyValue(PropertyValue):
    _type_map = {
        str: 'validate_str'
    }
    _set_field = 'select'

    init: Optional[str]
    select: SelectValue

    @classmethod
    def validate_str(cls, init: str):
        return SelectValue(name=init)


class StatusValue(BaseModel):
    status_id: Optional[str] = idField
    name: str
    color: Optional[str]


class StatusPropertyValue(PropertyValue):
    _type_map = {
        str: 'validate_str'
    }
    _set_field = 'status'

    init: Optional[str]
    status: StatusValue

    @classmethod
    def validate_str(cls, init: str):
        return StatusValue(name=init)


class MultiselectPropertyValue(PropertyValue):
    _type_map = {
        List: 'validate_str'
    }
    _set_field = 'multi_select'

    init: Optional[List[str]]
    multi_select: List[SelectValue]

    @classmethod
    def validate_str(cls, init: List[str]):
        return [SelectValue(name=init_item) for init_item in init]


class FileReferenceValue(BaseModel):
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


class DatePropertyValue(BaseModel):
    start: Union[datetime, date]
    end: Optional[Union[datetime, date]]
    time_zone: Optional[str]


class FormulaValue(BaseModel):
    formula_type: str = typeField
    string: Optional[str]
    number: Optional[float]
    date: Optional[datetime]
    boolean: Optional[bool]


class PageReferenceValue(BaseModel):
    page_id: str = idField


class RollupValue(BaseModel):
    rollup_type: str = typeField


def generate_value(property_type, value):
    _class_map = {
        "title": TitlePropertyValue,
        "rich_text": RichTextPropertyValue,
        "number": NumberPropertyValue,
        "select": SelectPropertyValue,
        "status": StatusPropertyValue,
        "multi_select": MultiselectPropertyValue,
    }
    value_cls = _class_map.get(property_type, None)
    if value_cls is None:
        raise NotImplementedError(
            f"Value generation for {property_type}"
            " property is not supporteed"
        )

    return value_cls(init=value)
