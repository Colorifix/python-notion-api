from typing import Optional, List, Dict

from pydantic import Field

from notion_integration.api.models.fields import (
    idField, typeField
)

from notion_integration.api.models.common import (
    RichTextObject
)

from notion_integration.api.models.values import (
    DatePropertyValue,
    SelectValue,
    FormulaValue,
    PageReferenceValue,
    RollupValue,
    StatusValue,
    FileReferenceValue
)

from notion_integration.api.models.objects import (
    User,
    NotionObject
)

from notion_integration.api.models.paginations import (
    PropertyItemPagination
)


class PropertyItem(NotionObject):
    property_id: str = idField
    propety_type: Optional[str] = typeField
    next_url: Optional[str]

    _class_map = {
        "number": "NumberPropertyItem",
        "select": "SelectPropertyItem",
        "multi_select": "MultiSelectPropertyItem",
        "status": "StatusPropertyItem",
        "date": "DatePropertyItem",
        "formula": "FormulaPropertyItem",
        "files": "FilesPropertyItem",
        "checkbox": "CheckBoxPropertyItem",
        "url": "URLPropertyItem",
        "email": "EmailPropertyItem",
        "phone_number": "PhoneNumberPropertyItem",
        "created_time": "CreatedTimePropertyItem",
        "created_by": "CreatedByPropertyItem",
        "last_edited_time": "LastEditedTimePropertyItem",
        "last_edited_by": "LastEditedByPropertyItem"
    }

    @property
    def _class_key_field(self):
        return self.propety_type


class TitlePropertyItem(PropertyItem):
    _class_key_field = None

    title: RichTextObject

    @property
    def value(self):
        return self.title.plain_text


class TitlePagination(PropertyItemPagination):
    _class_key_field = None

    results: List[TitlePropertyItem]


class RichTextPropertyItem(PropertyItem):
    _class_key_field = None

    rich_text: RichTextObject

    @property
    def value(self):
        return self.rich_text.plain_text


class RichTextPagination(PropertyItemPagination):
    _class_key_field = None

    results: List[RichTextPropertyItem]


class NumberPropertyItem(PropertyItem):
    _class_key_field = None

    number: Optional[float] = Field(...)

    @property
    def value(self):
        return self.number

    def set_value(self, value: float):
        self.number = value


class SelectPropertyItem(PropertyItem):
    _class_key_field = None

    select: Optional[SelectValue] = Field(...)

    @property
    def value(self):
        if self.select is not None:
            return self.select.name

    def set_value(self, value: float):
        self.select = SelectValue(name=value)


class StatusPropertyItem(PropertyItem):
    _class_key_field = None

    status: Optional[StatusValue] = Field(...)

    @property
    def value(self):
        if self.status is not None:
            return self.status.name


class MultiSelectPropertyItem(PropertyItem):
    _class_key_field = None

    multi_select: List[SelectValue]

    @property
    def value(self):
        return [so.name for so in self.multi_select]


class DatePropertyItem(PropertyItem):
    _class_key_field = None

    date: Optional[DatePropertyValue] = Field(...)

    @property
    def value(self):
        if self.date is not None:
            return self.date.start


class FormulaPropertyItem(PropertyItem):
    _class_key_field = None

    formula: Optional[FormulaValue] = Field(...)

    @property
    def value(self):
        return ''


class RelationPropertyItem(PropertyItem):
    _class_key_field = None

    relation: Optional[PageReferenceValue] = Field(...)

    @property
    def value(self):
        return self.relation.page_id


class RelationPagination(PropertyItemPagination):
    _class_key_field = None

    results: List[RelationPropertyItem]


class RollupPropertyItem(PropertyItem):
    _class_key_field = None

    rollup: RollupValue

    @property
    def value(self):
        return ''


class RollupPagination(PropertyItemPagination):
    _class_key_field = None

    results: List


class PeoplePropertyItem(PropertyItem):
    _class_key_field = None

    people: User

    @property
    def value(self):
        return self.people.name


class PeoplePagination(PropertyItemPagination):
    _class_key_field = None

    results: List[PeoplePropertyItem]


class FilesPropertyItem(PropertyItem):
    _class_key_field = None

    files: List[FileReferenceValue]

    @property
    def value(self):
        return [file.value for file in self.files]


class CheckBoxPropertyItem(PropertyItem):
    _class_key_field = None

    checkbox: Optional[bool] = Field(...)

    @property
    def value(self):
        return self.checkbox


class URLPropertyItem(PropertyItem):
    _class_key_field = None

    url: Optional[str] = Field(...)

    @property
    def value(self):
        return self.url


class EmailPropertyItem(PropertyItem):
    _class_key_field = None

    email: Optional[str] = Field(...)

    @property
    def value(self):
        return self.email


class PhoneNumberPropertyItem(PropertyItem):
    _class_key_field = None

    phone_number: Optional[str] = Field(...)

    @property
    def value(self):
        return self.phone_number


class CreatedTimePropertyItem(PropertyItem):
    _class_key_field = None

    created_time: str

    @property
    def value(self):
        return self.created_time


class CreatedByPropertyItem(PropertyItem):
    _class_key_field = None

    created_by: User

    @property
    def value(self):
        return self.created_by.name


class LastEditedTimePropertyItem(PropertyItem):
    _class_key_field = None

    last_edited_time: str

    @property
    def value(self):
        return self.last_edited_time


class LastEditedByPropertyItem(PropertyItem):
    _class_key_field = None

    last_edited_by: User

    @property
    def value(self):
        return self.last_edited_by.name
