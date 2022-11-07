from typing import Optional

from notion_integration.api.models.values import (
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
    URLPropertyValue
)

from notion_integration.api.models.objects import (
    User,
    NotionObject
)


class PropertyItem(NotionObject, PropertyValue):
    next_url: Optional[str]
    notion_object = 'property_item'
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
        "people": "PeoplePropertyItem",
        "relation": "RelationPropertyItem",
        "rollup": "RollupPropertyItem"
    }

    @property
    def _class_key_field(self):
        return self.property_type


class TitlePropertyItem(PropertyItem, TitlePropertyValue):
    _class_key_field = None
    property_type = 'title'


class RichTextPropertyItem(PropertyItem, RichTextPropertyValue):
    _class_key_field = None
    property_type = "rich_text"


class NumberPropertyItem(PropertyItem, NumberPropertyValue):
    _class_key_field = None
    property_type = 'number'


class SelectPropertyItem(PropertyItem, SelectPropertyValue):
    _class_key_field = None
    property_type = 'select'


class StatusPropertyItem(PropertyItem, StatusPropertyValue):
    _class_key_field = None
    property_type = 'status'


class MultiSelectPropertyItem(PropertyItem, MultiSelectPropertyValue):
    _class_key_field = None
    property_type = 'multi_select'


class DatePropertyItem(PropertyItem, DatePropertyValue):
    _class_key_field = None
    property_type = 'date'


class RelationPropertyItem(PropertyItem, RelationPropertyValue):
    _class_key_field = None
    property_type = 'relation'


class PeoplePropertyItem(PropertyItem, PeoplePropertyValue):
    _class_key_field = None
    property_type = 'people'


class FilesPropertyItem(PropertyItem, FilesPropertyValue):
    _class_key_field = None
    property_type = "files"


class CheckBoxPropertyItem(PropertyItem, CheckBoxPropertyValue):
    _class_key_field = None
    property_type = "checkbox"


class URLPropertyItem(PropertyItem, URLPropertyValue):
    _class_key_field = None
    property_type = "url"


class EmailPropertyItem(PropertyItem, EmailPropertyValue):
    _class_key_field = None
    property_type = "email"


class PhoneNumberPropertyItem(PropertyItem, PhoneNumberPropertyValue):
    _class_key_field = None
    property_type = "phone_number"


class FormulaPropertyItem(PropertyItem, FormulaPropertyValue):
    _class_key_field = None
    property_type = 'formula'


class CreatedTimePropertyItem(PropertyItem, CreatedTimePropertyValue):
    _class_key_field = None
    property_type = "created_time"


class CreatedByPropertyItem(PropertyItem, CreatedByPropertyValue):
    _class_key_field = None
    property_type = "created_by"


class LastEditedTimePropertyItem(PropertyItem, LastEditedTimePropertyValue):
    _class_key_field = None
    property_type = "last_edited_time"


class LastEditedByPropertyItem(PropertyItem, LastEditedByPropertyValue):
    _class_key_field = None
    property_type = "last_edited_by"


class RollupPropertyItem(PropertyItem, RollupPropertyValue):
    _class_key_field = None
    property_type = "rollup"
