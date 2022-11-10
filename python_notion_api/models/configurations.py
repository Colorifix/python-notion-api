from pydantic import BaseModel, Field
from typing import List, Dict, Optional

from notion_integration.api.models.fields import (
    idField, typeField
)

from notion_integration.api.models.objects import NotionObjectBase
from notion_integration.api.models.common import SelectObject

EmptyField = Optional[Dict]


class NotionPropertyConfiguration(NotionObjectBase):
    config_id: str = idField
    config_type: str = typeField
    name: str

    _class_map = {
        "title": "TitlePropertyConfiguration",
        "rich_text": "TextPropertyConfiguration",
        "number": "NumberPropertyConfiguration",
        "select": "SelectPropertyConfiguration",
        "multi_select": "MultiSelectPropertyConfiguration",
        "date": "DatePropertyConfiguration",
        "people": "PeoplePropertyConfiguration",
        "files": "FilesPropertyConfiguration",
        "checkbox": "CheckBoxPropertyConfiguration",
        "url": "URLPropertyConfiguration",
        "email": "EmailPropertyConfiguration",
        "phone_number": "PhoneNumberPropertyConfiguration",
        "formula": "FormulaPropertyConfiguration",
        "relation": "RelationPropertyConfiguration",
        "rollup": "RollupPropertyConfiguration",
        "created_time": "CreatedTimePropertyConfiguration",
        "created_by": "CreatedByPropertyConfiguration",
        "last_edited_time": "LastEditedTimePropertyConfiguration",
        "last_edited_by": "LastEditedTimePropertyConfiguration",
        "status": "StatusPropertyConfiguration"
    }

    @property
    def _class_key_field(self):
        return self.config_type


class TitlePropertyConfiguration(NotionPropertyConfiguration):
    _class_key_field = None

    title: EmptyField


class TextPropertyConfiguration(NotionPropertyConfiguration):
    _class_key_field = None

    rich_text: EmptyField


class NumberPropertyConfiguration(NotionPropertyConfiguration):
    _class_key_field = None

    number_format: Optional[str] = Field(alias="format", default='')


class SelectPropertyConfiguration(NotionPropertyConfiguration):
    _class_key_field = None

    options: Optional[List[SelectObject]] = []


class StatusPropertyConfiguration(NotionPropertyConfiguration):
    _class_key_field = None

    staus: EmptyField


class MultiSelectPropertyConfiguration(NotionPropertyConfiguration):
    _class_key_field = None

    options: Optional[List[SelectObject]] = []


class DatePropertyConfiguration(NotionPropertyConfiguration):
    _class_key_field = None

    date: EmptyField


class PeoplePropertyConfiguration(NotionPropertyConfiguration):
    _class_key_field = None

    people: EmptyField


class FilesPropertyConfiguration(NotionPropertyConfiguration):
    _class_key_field = None

    files: EmptyField


class CheckBoxPropertyConfiguration(NotionPropertyConfiguration):
    _class_key_field = None

    checkbox: EmptyField


class URLPropertyConfiguration(NotionPropertyConfiguration):
    _class_key_field = None

    url: EmptyField


class EmailPropertyConfiguration(NotionPropertyConfiguration):
    _class_key_field = None

    email: EmptyField


class PhoneNumberPropertyConfiguration(NotionPropertyConfiguration):
    _class_key_field = None

    phone_number: EmptyField


class FormulaConfigurationObject(BaseModel):
    expression: str


class FormulaPropertyConfiguration(NotionPropertyConfiguration):
    _class_key_field = None

    formula: FormulaConfigurationObject


class RelationConfigurationObject(BaseModel):
    database_id: str
    synced_property_name: Optional[str]
    synced_property_id: Optional[str]


class RelationPropertyConfiguration(NotionPropertyConfiguration):
    _class_key_field = None

    relation: RelationConfigurationObject


class RollupConfigurationObject(BaseModel):
    relation_property_name: str
    relation_property_id: str
    rollup_property_name: str
    rollup_property_id: str
    function: str


class RollupPropertyConfiguration(NotionPropertyConfiguration):
    _class_key_field = None

    rollup: RollupConfigurationObject


class CreatedTimePropertyConfiguration(NotionPropertyConfiguration):
    _class_key_field = None

    created_time: EmptyField


class CreatedByPropertyConfiguration(NotionPropertyConfiguration):
    _class_key_field = None

    created_by: EmptyField


class LastEditedTimePropertyConfiguration(NotionPropertyConfiguration):
    _class_key_field = None

    last_edited_time: EmptyField


class LastEditedByPropertyConfiguration(NotionPropertyConfiguration):
    _class_key_field = None

    last_edited_by: EmptyField
