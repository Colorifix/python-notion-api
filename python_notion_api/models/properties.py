from typing import Optional

from pydantic import Field

from python_notion_api.models.objects import NotionObject
from python_notion_api.models.values import (
    CheckBoxPropertyValue,
    CreatedByPropertyValue,
    CreatedTimePropertyValue,
    DatePropertyValue,
    EmailPropertyValue,
    FilesPropertyValue,
    FormulaPropertyValue,
    LastEditedByPropertyValue,
    LastEditedTimePropertyValue,
    MultiSelectPropertyValue,
    NumberPropertyValue,
    PeoplePropertyValue,
    PhoneNumberPropertyValue,
    PropertyValue,
    RelationPropertyValue,
    RichTextPropertyValue,
    RollupPropertyValue,
    SelectPropertyValue,
    StatusPropertyValue,
    TitlePropertyValue,
    UniqueIDPropertyValue,
    URLPropertyValue,
)


class PropertyItem(NotionObject, PropertyValue):
    next_url: Optional[str]
    notion_object = "property_item"
    has_more: Optional[bool] = False

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
        "relation": "RelationPropertyItem",
        "rollup": "RollupPropertyItem",
        "unique_id": "UniqueIDPropertyItem",
    }

    @property
    def _class_key_field(self):
        return self.property_type


class TitlePropertyItem(PropertyItem, TitlePropertyValue):
    _class_key_field = None
    property_type: str = Field(alias="type", default="title")


class RichTextPropertyItem(PropertyItem, RichTextPropertyValue):
    _class_key_field = None
    property_type: str = Field(alias="type", default="rich_text")


class NumberPropertyItem(PropertyItem, NumberPropertyValue):
    _class_key_field = None
    property_type: str = Field(alias="type", default="number")


class SelectPropertyItem(PropertyItem, SelectPropertyValue):
    _class_key_field = None
    property_type: str = Field(alias="type", default="select")


class StatusPropertyItem(PropertyItem, StatusPropertyValue):
    _class_key_field = None
    property_type: str = Field(alias="type", default="status")


class MultiSelectPropertyItem(PropertyItem, MultiSelectPropertyValue):
    _class_key_field = None
    property_type: str = Field(alias="type", default="multi_select")


class DatePropertyItem(PropertyItem, DatePropertyValue):
    _class_key_field = None
    property_type: str = Field(alias="type", default="date")


class RelationPropertyItem(PropertyItem, RelationPropertyValue):
    _class_key_field = None
    property_type: str = Field(alias="type", default="relation")


class PeoplePropertyItem(PropertyItem, PeoplePropertyValue):
    _class_key_field = None
    property_type: str = Field(alias="type", default="people")


class FilesPropertyItem(PropertyItem, FilesPropertyValue):
    _class_key_field = None
    property_type: str = Field(alias="type", default="files")


class CheckBoxPropertyItem(PropertyItem, CheckBoxPropertyValue):
    _class_key_field = None
    property_type: str = Field(alias="type", default="checkbox")


class URLPropertyItem(PropertyItem, URLPropertyValue):
    _class_key_field = None
    property_type: str = Field(alias="type", default="url")


class EmailPropertyItem(PropertyItem, EmailPropertyValue):
    _class_key_field = None
    property_type: str = Field(alias="type", default="email")


class PhoneNumberPropertyItem(PropertyItem, PhoneNumberPropertyValue):
    _class_key_field = None
    property_type: str = Field(alias="type", default="phone_number")


class FormulaPropertyItem(PropertyItem, FormulaPropertyValue):
    _class_key_field = None
    property_type: str = Field(alias="type", default="formula")


class CreatedTimePropertyItem(PropertyItem, CreatedTimePropertyValue):
    _class_key_field = None
    property_type: str = Field(alias="type", default="created_time")


class CreatedByPropertyItem(PropertyItem, CreatedByPropertyValue):
    _class_key_field = None
    property_type: str = Field(alias="type", default="created_by")


class LastEditedTimePropertyItem(PropertyItem, LastEditedTimePropertyValue):
    _class_key_field = None
    property_type: str = Field(alias="type", default="last_edited_time")


class LastEditedByPropertyItem(PropertyItem, LastEditedByPropertyValue):
    _class_key_field = None
    property_type: str = Field(alias="type", default="last_edited_by")


class RollupPropertyItem(PropertyItem, RollupPropertyValue):
    _class_key_field = None
    property_type: str = Field(alias="type", default="rollup")


class UniqueIDPropertyItem(PropertyItem, UniqueIDPropertyValue):
    _class_key_field = None
    property_type: str = Field(alias="type", default="unique_id")
