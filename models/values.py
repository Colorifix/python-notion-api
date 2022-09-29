from datetime import date, datetime
from typing import ClassVar, List, Optional, Tuple, Union
from uuid import UUID

from notion_integration.api.models.common import (DateObject, File, FileObject,
                                                  RelationObject,
                                                  RichTextObject, SelectObject,
                                                  StatusObject)
from notion_integration.api.models.fields import idField, typeField
from notion_integration.api.models.objects import User
from notion_integration.gdrive import GDrive
from pydantic import (BaseModel, Field, ValidationError, parse_obj_as,
                      root_validator, AnyUrl, FilePath)
from typing_extensions import Annotated


def excluded(field_type):
    return Annotated[field_type, Field(exclude=True)]


class PropertyValue(BaseModel):
    _type_map: ClassVar
    _set_field: ClassVar[str]

    @root_validator(pre=True)
    def validate_init(cls, values):
        init = values.get('init', None)
        for check_type, method_name in cls._type_map.items():
            try:
                obj = parse_obj_as(check_type, init)
                values[cls._set_field] = getattr(cls, method_name)(obj)
                break
            except ValidationError:
                pass
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

    init: excluded(Optional[Union[RichTextObject, str, List[RichTextObject]]])
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

    init: excluded(Optional[Union[RichTextObject, str, List[RichTextObject]]])
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

    init: excluded(Optional[Union[float, int]])
    number: float


class SelectPropertyValue(PropertyValue):
    _type_map = {
        str: 'validate_str'
    }
    _set_field = 'select'

    init: excluded(Optional[str])
    select: SelectObject

    @classmethod
    def validate_str(cls, init: str):
        return SelectObject(name=init)


class StatusPropertyValue(PropertyValue):
    _type_map = {
        str: 'validate_str'
    }
    _set_field = 'status'

    init: excluded(Optional[str])
    status: StatusObject

    @classmethod
    def validate_str(cls, init: str):
        return StatusObject(name=init)


class MultiselectPropertyValue(PropertyValue):
    _type_map = {
        List: 'validate_str'
    }
    _set_field = 'multi_select'

    init: excluded(Optional[List[str]])
    multi_select: List[SelectObject]

    @classmethod
    def validate_str(cls, init: List[str]):
        return [SelectObject(name=init_item) for init_item in init]


class DatePropertyValue(PropertyValue):
    _type_map = {
        datetime: 'validate_date',
        date: 'validate_date',
        str: 'validate_str',
        DateObject: 'leave_unchanged',
        Tuple[datetime, datetime]:
            'validate_date_tuple',
        Tuple[str, str]: 'validate_str_tuple'
    }

    _set_field = 'date'

    init: excluded(Optional[Union[
        datetime, date,
        str, DateObject,
        Tuple[datetime, datetime],
        Tuple[str, str]
    ]])
    date: DateObject

    @classmethod
    def validate_date(cls, init: datetime):
        return DateObject(start=init)

    @classmethod
    def validate_str(cls, init: str):
        try:
            date_obj = datetime.fromisoformat(init)
            return DateObject(start=date_obj)
        except ValueError as e:
            raise (
                ValidationError("Suppied date string is not in iso format")
            ) from e

    @classmethod
    def validate_date_tuple(
        cls,
        init: Tuple[datetime, datetime]
    ):
        return DateObject(start=init[0], end=init[1])

    @classmethod
    def validate_str_tuple(cls, init: Tuple[str, str]):
        try:
            start = datetime.fromisoformat(init[0])
            end = datetime.fromisoformat(init[1])
            return DateObject(start=start, end=end)
        except ValueError as e:
            raise (
                ValidationError("Suppied date string is not in iso format")
            ) from e


class PeoplePropertyValue(PropertyValue):
    _type_map = {
        List[str]: "validate_str",
        List[User]: "leave_unchanged"
    }
    _set_field = 'people'

    init: excluded(Optional[Union[List[str], List[User]]])
    people: List[User]

    @classmethod
    def validate_str(cls, init: List[str]):
        users = []
        for value in init:
            uuid = UUID(value)
            users.append(User.from_id(str(uuid)))
        return users


class FilePropertyValue(PropertyValue):
    _type_map = {
        FilePath: "validate_file_path",
        List[File]: "validate_file"
    }

    _set_field = 'files'

    init: excluded(Optional[List[File]])
    files: List[FileObject]

    @classmethod
    def validate_file(cls, init: List[File]):
        files = []
        for value in init:
            files.append(FileObject.from_file(value))
        return files


class CheckboxPropertyValue(PropertyValue):
    _type_map = {
        bool: "leave_unchanged"
    }

    _set_field = 'checkbox'

    init: excluded(Optional[bool])
    checkbox: bool


class URLPropertyValue(PropertyValue):
    _type_map = {
        AnyUrl: "leave_unchanged",
        FilePath: "validate_file_path",
        File: "validate_file"
    }
    _set_field = 'url'

    init: excluded(Optional[Union[AnyUrl, FilePath, File]])
    url: str

    @classmethod
    def validate_file_path(cls, init: FilePath):
        return File.from_file_path(init).url

    @classmethod
    def validate_file(cls, init: File):
        return init.url


class EmailPropertyValue(PropertyValue):
    _type_map = {
        str: "leave_unchanged"
    }
    _set_field = 'email'

    init: excluded(Optional[str])
    email: str


class PhoneNumberPropertyValue(PropertyValue):
    _type_map = {
        str: "leave_unchanged"
    }
    _set_field = 'phone_number'

    init: excluded(Optional[str])
    phone_number: str


class RelationPropertyValue(PropertyValue):
    _type_map = {
        List[str]: "validate_str"
    }
    _set_field = 'relation'

    init: excluded(Optional[List[str]])
    relation: List[RelationObject]

    @classmethod
    def validate_str(cls, init: List[str]):
        return [RelationObject(id=value) for value in init]


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
        "date": DatePropertyValue,
        "people": PeoplePropertyValue,
        "files": FilePropertyValue,
        "checkbox": CheckboxPropertyValue,
        "url": URLPropertyValue,
        "email": EmailPropertyValue,
        "phone_number": PhoneNumberPropertyValue,
        "relation": RelationPropertyValue
    }
    value_cls = _class_map.get(property_type, None)
    if value_cls is None:
        raise NotImplementedError(
            f"Value generation for {property_type}"
            " property is not supporteed"
        )

    return value_cls(init=value)
