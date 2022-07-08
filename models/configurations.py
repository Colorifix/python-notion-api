from pydantic import BaseModel, Field
from typing import List, Dict, Optional

from notion_integration.api.models.fields import (
    idField, typeField, formatField
)

from notion_integration.api.models.objects import (
    SelectObject, FormulaConfigurationObject,
    RelationConfigurationObject,
    RollupConfigurationObject
)

EmptyField = Optional[Dict]

config_map = {
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


class NotionPropertyConfiguration(BaseModel):
    config_id: str = idField
    config_type: str = typeField
    name: str

    @classmethod
    def from_obj(cls, obj):
        for config_key, config_class_name in config_map.items():
            if config_key in obj:
                config_cls = cls._get_config_cls(config_class_name)
                if config_cls is None:
                    raise ValueError(f"{config_class_name} is unknown")
                return config_cls(**obj)

    @staticmethod
    def _get_config_cls(cls_name):
        return next((
            cls for cls in NotionPropertyConfiguration.__subclasses__()
            if cls.__name__ == cls_name
        ), None)


class TitlePropertyConfiguration(NotionPropertyConfiguration):
    title: EmptyField


class TextPropertyConfiguration(NotionPropertyConfiguration):
    rich_text: EmptyField


class NumberPropertyConfiguration(NotionPropertyConfiguration):
    number_format: Optional[str] = Field(alias="format", default='')


class SelectPropertyConfiguration(NotionPropertyConfiguration):
    options: Optional[List[SelectObject]] = []


class StatusPropertyConfiguration(NotionPropertyConfiguration):
    staus: EmptyField


class MultiSelectPropertyConfiguration(NotionPropertyConfiguration):
    options: Optional[List[SelectObject]] = []


class DatePropertyConfiguration(NotionPropertyConfiguration):
    date: EmptyField


class PeoplePropertyConfiguration(NotionPropertyConfiguration):
    people: EmptyField


class FilesPropertyConfiguration(NotionPropertyConfiguration):
    files: EmptyField


class CheckBoxPropertyConfiguration(NotionPropertyConfiguration):
    checkbox: EmptyField


class URLPropertyConfiguration(NotionPropertyConfiguration):
    url: EmptyField


class EmailPropertyConfiguration(NotionPropertyConfiguration):
    email: EmptyField


class PhoneNumberPropertyConfiguration(NotionPropertyConfiguration):
    phone_number: EmptyField


class FormulaPropertyConfiguration(NotionPropertyConfiguration):
    formula: FormulaConfigurationObject


class RelationPropertyConfiguration(NotionPropertyConfiguration):
    relation: RelationConfigurationObject


class RollupPropertyConfiguration(NotionPropertyConfiguration):
    rollup: RollupConfigurationObject


class CreatedTimePropertyConfiguration(NotionPropertyConfiguration):
    created_time: EmptyField


class CreatedByPropertyConfiguration(NotionPropertyConfiguration):
    created_by: EmptyField


class LastEditedTimePropertyConfiguration(NotionPropertyConfiguration):
    last_edited_time: EmptyField


class LastEditedByPropertyConfiguration(NotionPropertyConfiguration):
    last_edited_by: EmptyField
