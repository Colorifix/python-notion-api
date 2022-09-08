from loguru import logger

from typing import Optional, List

from pydantic import Field

from notion_integration.api.models.fields import (
    idField, typeField
)

from notion_integration.api.models.common import (
    RichTextObject,
    SelectObject,
    StatusObject,
    DateObject,
    FileObject,
    File
)

from notion_integration.api.models.values import (
    FormulaValue,
    PageReferenceValue
)

from notion_integration.api.models.objects import (
    User,
    NotionObject
)


class PropertyItem(NotionObject):
    property_id: Optional[str] = idField
    property_type: Optional[str] = typeField
    next_url: Optional[str]
    notion_object = 'property_item'

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
        "last_edited_by": "LastEditedByPropertyItem",
        "people": "PeoplePropertyItem",
        "title": "TitlePropertyItem",
        "rich_text": "RichTextPropertyItem",
        "people": "PeoplePropertyItem",
        "relation": "RelationPropertyItem"
    }

    @property
    def _class_key_field(self):
        return self.property_type


class TitlePropertyItem(PropertyItem):
    _class_key_field = None
    property_type = 'title'

    title: RichTextObject

    @property
    def value(self) -> str:
        return self.title.plain_text


class RichTextPropertyItem(PropertyItem):
    _class_key_field = None
    property_type = "rich_text"

    rich_text: RichTextObject

    @property
    def value(self):
        return self.rich_text.plain_text


class NumberPropertyItem(PropertyItem):
    _class_key_field = None
    property_type = 'number'

    number: Optional[float] = Field(...)

    @property
    def value(self):
        return self.number


class SelectPropertyItem(PropertyItem):
    _class_key_field = None
    property_type = 'select'

    select: Optional[SelectObject] = Field(...)

    @property
    def value(self):
        if self.select is not None:
            return self.select.name


class StatusPropertyItem(PropertyItem):
    _class_key_field = None
    property_type = 'status'

    status: Optional[StatusObject] = Field(...)

    @property
    def value(self):
        if self.status is not None:
            return self.status.name


class MultiSelectPropertyItem(PropertyItem):
    _class_key_field = None
    property_type = 'multi_select'

    multi_select: List[SelectObject]

    @property
    def value(self):
        return [so.name for so in self.multi_select]


class DatePropertyItem(PropertyItem):
    _class_key_field = None
    property_type = 'date'

    date: Optional[DateObject] = Field(...)

    @property
    def value(self):
        if self.date is not None:
            return self.date


class FormulaPropertyItem(PropertyItem):
    _class_key_field = None
    property_type = 'formula'

    formula: Optional[FormulaValue] = Field(...)

    @property
    def value(self):
        val = getattr(self.formula, self.formula.formula_type)
        logger.warning(
            f'Returning formula value {val}, which might be incorrect'
        )
        return val


class RelationPropertyItem(PropertyItem):
    _class_key_field = None
    property_type = 'relation'

    relation: Optional[PageReferenceValue] = Field(...)

    @property
    def value(self):
        return self.relation.page_id


class PeoplePropertyItem(PropertyItem):
    _class_key_field = None

    people: User

    @property
    def value(self):
        return self.people.name


class FilesPropertyItem(PropertyItem):
    _class_key_field = None
    property_type = "files"

    files: List[FileObject]

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


class CheckBoxPropertyItem(PropertyItem):
    _class_key_field = None
    property_type = "checkbox"

    checkbox: Optional[bool] = Field(...)

    @property
    def value(self):
        return self.checkbox


class URLPropertyItem(PropertyItem):
    _class_key_field = None
    property_type = "url"

    url: Optional[str] = Field(...)

    @property
    def value(self):
        return self.url


class EmailPropertyItem(PropertyItem):
    _class_key_field = None
    property_type = "email"

    email: Optional[str] = Field(...)

    @property
    def value(self):
        return self.email


class PhoneNumberPropertyItem(PropertyItem):
    _class_key_field = None
    property_type = "phone_number"

    phone_number: Optional[str] = Field(...)

    @property
    def value(self):
        return self.phone_number


class CreatedTimePropertyItem(PropertyItem):
    _class_key_field = None
    property_type = "created_time"

    created_time: str

    @property
    def value(self):
        return self.created_time


class CreatedByPropertyItem(PropertyItem):
    _class_key_field = None
    property_type = "created_by"

    created_by: User

    @property
    def value(self):
        return self.created_by.name


class LastEditedTimePropertyItem(PropertyItem):
    _class_key_field = None
    property_type = "last_edited_time"

    last_edited_time: str

    @property
    def value(self):
        return self.last_edited_time


class LastEditedByPropertyItem(PropertyItem):
    _class_key_field = None
    property_type = "last_edited_by"

    last_edited_by: User

    @property
    def value(self):
        return self.last_edited_by.name
