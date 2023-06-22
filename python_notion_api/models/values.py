from datetime import date, datetime
from typing import ClassVar, Dict, List, Optional, Tuple, Union, Any
from uuid import UUID

from loguru import logger

from python_notion_api.models.common import (
    DateObject, File, FileObject, FormulaObject, RelationObject,
    RichTextObject, RollupObject, SelectObject, StatusObject,
    UniqueIDObject
)
from python_notion_api.models.objects import User
from pydantic import (BaseModel, Field, ValidationError, parse_obj_as,
                      root_validator, AnyUrl, FilePath)
from typing_extensions import Annotated


def excluded(field_type):
    return Annotated[field_type, Field(exclude=True)]


class PropertyValue(BaseModel):
    property_id: Optional[str] = Field(alias="id", exclude=True)
    property_type: Optional[str] = Field(alias="type", exclude=True)

    _type_map: ClassVar
    _set_field: ClassVar[str]

    @root_validator(pre=True)
    def validate_init(cls, values):
        init = values.get('init', None)
        if init is not None:
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

    @classmethod
    def from_property_item(cls, obj):
        derived_cls = get_value_class(obj.property_type)
        if derived_cls is None:
            raise NotImplementedError(
                f"Proerty type {obj.property_type}"
                " is not supported"
            )
        return derived_cls(**{
            'type': obj.property_type,
            'id': obj.property_id,
            obj.property_type: getattr(obj, obj.property_type)
        })


class TitlePropertyValue(PropertyValue):
    _type_map = {
        str: 'validate_str',
        List[RichTextObject]: 'leave_unchanged',
        RichTextObject: 'validate_rich_text'
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

    @property
    def value(self):
        return "".join([
            element.plain_text
            for element in self.title
        ])


class RichTextPropertyValue(PropertyValue):
    _type_map = {
        str: 'validate_str',
        List[RichTextObject]: 'leave_unchanged',
        RichTextObject: 'validate_rich_text'
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

    @property
    def value(self):
        return "".join([
            element.plain_text
            for element in self.rich_text
        ])


class NumberPropertyValue(PropertyValue):
    _type_map = {
        float: 'leave_unchanged',
        int: 'leave_unchanged',
    }
    _set_field = 'number'

    init: excluded(Optional[Union[float, int]])
    number: Optional[float]

    @property
    def value(self):
        return self.number


class SelectPropertyValue(PropertyValue):
    _type_map = {
        SelectObject: 'leave_unchanged',
        str: 'validate_str'
    }
    _set_field = 'select'

    init: excluded(Optional[Union[SelectObject, str]])
    select: Optional[SelectObject]

    @classmethod
    def validate_str(cls, init: str):
        return SelectObject(name=init)

    @property
    def value(self):
        if self.select is not None:
            return self.select.name


class StatusPropertyValue(PropertyValue):
    _type_map = {
        StatusObject: 'leave_unchanged',
        str: 'validate_str'
    }
    _set_field = 'status'

    init: excluded(Optional[Union[StatusObject, str]])
    status: Optional[StatusObject]

    @classmethod
    def validate_str(cls, init: str):
        return StatusObject(name=init)

    @property
    def value(self):
        if self.status is not None:
            return self.status.name


class MultiSelectPropertyValue(PropertyValue):
    _type_map = {
        List[SelectObject]: 'leave_unchanged',
        List: 'validate_str'
    }
    _set_field = 'multi_select'

    init: excluded(Optional[Union[List[SelectObject], List[str]]])
    multi_select: List[SelectObject]

    @classmethod
    def validate_str(cls, init: List[str]):
        return [SelectObject(name=init_item) for init_item in init]

    @property
    def value(self):
        return [so.name for so in self.multi_select]


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
    date: Optional[DateObject]

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

    @property
    def value(self):
        if self.date is not None:
            return self.date


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

    @property
    def value(self):
        return [so.name for so in self.people]


class FilesPropertyValue(PropertyValue):
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

    @property
    def value(self):
        files = []
        for file_object in self.files:
            name = file_object.name
            if file_object.reference_type == "external":
                files.append(File(name=name, url=file_object.external.url))
            else:
                files.append(File(name=name, url=file_object.file.url))
        return files


class CheckBoxPropertyValue(PropertyValue):
    _type_map = {
        bool: "leave_unchanged"
    }

    _set_field = 'checkbox'

    init: excluded(Optional[bool])
    checkbox: bool

    @property
    def value(self):
        return self.checkbox


class URLPropertyValue(PropertyValue):
    _type_map = {
        AnyUrl: "leave_unchanged",
        FilePath: "validate_file_path",
        File: "validate_file"
    }
    _set_field = 'url'

    init: excluded(Optional[Union[AnyUrl, FilePath, File]])
    url: Optional[str]

    @classmethod
    def validate_file_path(cls, init: FilePath):
        return File.from_file_path(init).url

    @classmethod
    def validate_file(cls, init: File):
        return init.url

    @property
    def value(self):
        return self.url


class EmailPropertyValue(PropertyValue):
    _type_map = {
        str: "leave_unchanged"
    }
    _set_field = 'email'

    init: excluded(Optional[str])
    email: Optional[str]

    @property
    def value(self):
        return self.email


class PhoneNumberPropertyValue(PropertyValue):
    _type_map = {
        str: "leave_unchanged"
    }
    _set_field = 'phone_number'

    init: excluded(Optional[str])
    phone_number: Optional[str]

    @property
    def value(self):
        return self.phone_number


class RelationPropertyValue(PropertyValue):
    _type_map = {
        List[RelationObject]: "leave_unchanged",
        List[str]: "validate_list",
        str: "validate_str",
        RelationObject: "validate_relation"
    }
    _set_field = 'relation'

    init: excluded(Optional[
        Union[List[RelationObject], List[str], RelationObject, str]
    ])
    relation: List[RelationObject]

    @classmethod
    def validate_list(cls, init: List[str]):
        return [RelationObject(id=value) for value in init]

    @classmethod
    def validate_str(cls, init: str):
        return [RelationObject(id=init)]

    @property
    def value(self):
        return [element.relation_id for element in self.relation]

    @classmethod
    def validate_relation(cls, init: RelationObject):
        return [init]


class FormulaPropertyValue(PropertyValue):
    _type_map = {
        FormulaObject: "leave_unchanged",
    }
    _set_field = 'formula'

    init: excluded(Optional[FormulaObject])
    formula: Optional[FormulaObject]

    @property
    def value(self):
        val = getattr(self.formula, self.formula.formula_type)
        logger.warning(
            f'Returning formula value {val}, which might be incorrect'
        )
        return val


class RollupPropertyValue(PropertyValue):
    _type_map = {
        RollupObject: "leave_unchanged",
        List: "validate_array"
    }
    _set_field = 'rollup'

    init: excluded(Optional[Union[List, RollupObject]])
    rollup: RollupObject

    @classmethod
    def validate_array(cls, init: List):
        if len(init) == 0:
            return RollupObject(
                function="show_original",
                type="array",
                array=[]
            )

        first_item = init[0]

        from python_notion_api.models import PropertyItem

        if isinstance(first_item, PropertyItem):
            init = [item.dict(by_alias=True) for item in init]

        return RollupObject(
            function="show_original",
            type="array",
            array=init
        )

    @property
    def value(self):
        rollup_type = self.rollup.rollup_type
        if rollup_type == 'array':
            items = []
            for item in self.rollup.array:
                cls_value = get_value_class(item["type"])
                if cls_value is None:
                    raise ValueError("Got an unknown rollup value.")
                items.append(cls_value(**item).value)
            return items
        elif rollup_type == 'number':
            return self.rollup.number
        elif rollup_type == 'date':
            return self.rollup.date
        else:
            raise ValueError("Got an incomplete rollup. Sorry")


class CreatedTimePropertyValue(PropertyValue):
    _type_map = {
        Dict[str, Any]: "leave_unchanged",
    }
    _set_field = 'created_time'

    init: excluded(Optional[str])
    created_time: str

    @property
    def value(self):
        return self.created_time


class LastEditedTimePropertyValue(PropertyValue):
    _type_map = {
        Dict[str, Any]: "leave_unchanged",
    }
    _set_field = 'last_edited_time'

    init: excluded(Optional[str])
    last_edited_time: str

    @property
    def value(self):
        return self.last_edited_time


class CreatedByPropertyValue(PropertyValue):
    _type_map = {
        User: "leave_unchanged",
    }
    _set_field = 'created_by'

    init: excluded(Optional[User])
    created_by: User

    @property
    def value(self):
        return self.created_by.name


class LastEditedByPropertyValue(PropertyValue):
    _type_map = {
        User: "leave_unchanged",
    }
    _set_field = 'last_edited_by'

    init: excluded(Optional[User])
    last_edited_by: User

    @property
    def value(self):
        return self.last_edited_by.name


class UniqueIDPropertyValue(PropertyValue):
    _type_map = {
        UniqueIDObject: "leave_unchanged",
        int: "validate_int",
        str: "validate_str"
    }

    _set_field = 'unique_id'

    init: excluded(Optional[Union[int, str, UniqueIDObject]])
    unique_id: UniqueIDObject

    @classmethod
    def validate_int(cls, init: int):
        return UniqueIDObject(
            number=init
        )

    @classmethod
    def validate_str(cls, init: str):
        parts = init.split('-')
        return UniqueIDObject(
            prefix=parts[0],
            number=int(parts[1])
        )

    @property
    def value(self):
        return self.unique_id.number


def get_value_class(property_type):
    _class_map = {
        "title": TitlePropertyValue,
        "rich_text": RichTextPropertyValue,
        "number": NumberPropertyValue,
        "select": SelectPropertyValue,
        "status": StatusPropertyValue,
        "multi_select": MultiSelectPropertyValue,
        "date": DatePropertyValue,
        "people": PeoplePropertyValue,
        "files": FilesPropertyValue,
        "checkbox": CheckBoxPropertyValue,
        "url": URLPropertyValue,
        "email": EmailPropertyValue,
        "phone_number": PhoneNumberPropertyValue,
        "relation": RelationPropertyValue,
        "last_edited_by": LastEditedByPropertyValue,
        "created_by": CreatedByPropertyValue,
        "last_edited_time": LastEditedTimePropertyValue,
        "created_time": CreatedTimePropertyValue,
        "rollup": RollupPropertyValue,
        "formula": FormulaPropertyValue,
        "unique_id": UniqueIDPropertyValue
    }
    return _class_map.get(property_type, None)


def generate_value(property_type, value):
    value_cls = get_value_class(property_type)
    if value_cls is None:
        raise NotImplementedError(
            f"Value generation for {property_type}"
            " property is not supported"
        )

    return value_cls(init=value)
