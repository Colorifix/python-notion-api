from pydantic import BaseModel, Extra, ValidationError
from typing import Optional, Literal, List, Dict

from notion_integration.api.models.fields import (
    idField, typeField, objectField
)

from notion_integration.api.models.objects import (
    UserObject,
    DatePropertyValueObject,
    RichTextObject,
    SelectObject,
    FormulaObject,
    PageReferenceObject,
    RollupObject,
    StatusObject,
    FileReferenceObject
)

property_map = {
    "rich_text": "RichTextProperty",
    "number": "NumberProperty",
    "select": "SelectProperty",
    "multi_select": "MultiSelectProperty",
    "status": "StatusProperty",
    "date": "DateProperty",
    "formula": "FormulaProperty",
    "relation": "RelationProperty",
    "rollup": "RollupProperty",
    "title": "TitleProperty",
    "people": "PeopleProperty",
    "files": "FilesProperty",
    "checkbox": "CheckBoxProperty",
    "url": "URLProperty",
    "email": "EmailProperty",
    "phone_number": "PhoneNumberProperty",
    "created_time": "CreatedTimeProperty",
    "created_by": "CreatedByProperty",
    "last_edited_time": "LastEditedTimeProperty",
    "last_edited_by": "LastEditedByProperty"
}


class PaginationObject(BaseModel):
    has_more: bool
    next_cursor: str
    results: List
    paginaton_object: Literal["object"] = objectField
    pagination_type: Literal[
        "block", "page", "user", "database", "property_item",
        "page_or_database"
    ] = typeField


class PropertyItemPaginationObject(PaginationObject):
    pagination_item: Dict


class NotionPropertyItemObject(BaseModel, extra=Extra.allow):
    property_object: str = objectField
    property_id: str = idField
    propety_type: Optional[str] = typeField
    next_url: Optional[str]

    @classmethod
    def from_obj(cls, obj):
        for propery_key, property_class_name in property_map.items():
            if propery_key in obj:
                prop_cls = cls._get_propetry_cls(property_class_name)
                if prop_cls is None:
                    raise ValueError(f"{property_class_name} is unknown")
                try:
                    prop = prop_cls(**obj)
                except Exception:
                    breakpoint()
                return prop

    @staticmethod
    def _get_propetry_cls(cls_name):
        return next((
            cls for cls in NotionPropertyValue.__subclasses__()
            if cls.__name__ == cls_name
        ), None)


class TitlePropertyValue(NotionPropertyValue):
    title: List[RichTextObject]

    @property
    def value(self):
        return "".join([rto.plain_text for rto in self.title])


class RichTextPropertyValue(NotionPropertyValue):
    rich_text: List[RichTextObject]

    @property
    def value(self):
        return "".join([rto.plain_text for rto in self.rich_text])


class NumberPropertyValue(NotionPropertyValue):
    number: float

    @property
    def value(self):
        return self.number


class SelectPropertyValue(NotionPropertyValue):
    select: SelectObject

    @property
    def value(self):
        return self.select.name


class StatusPropertyValue(NotionPropertyValue):
    status: StatusObject

    @property
    def value(self):
        return self.status.name


class MultiSelectPropertyValue(NotionPropertyValue):
    multi_select: List[SelectObject]

    @property
    def value(self):
        return [so.name for so in self.multi_select]


class DatePropertyValue(NotionPropertyValue):
    date: DatePropertyValueObject

    @property
    def value(self):
        return self.date.start


class FormulaPropertyValue(NotionPropertyValue):
    formula: FormulaObject

    @property
    def value(self):
        return ''


class RelationPropertyValue(NotionPropertyValue):
    relation: List[PageReferenceObject]

    @property
    def value(self):
        return [pr.page_id for pr in self.relation]


class RollupPropertyValue(NotionPropertyValue):
    rollup: RollupObject

    @property
    def value(self):
        return ''


class PeoplePropertyValue(NotionPropertyValue):
    people: List[UserObject]

    @property
    def value(self):
        return [p.name for p in self.people]


class FilesPropertyValue(NotionPropertyValue):
    files: List[FileReferenceObject]

    @property
    def value(self):
        return [file.value for file in self.files] 


class CheckBoxPropertyValue(NotionPropertyValue):
    checkbox: bool

    @property
    def value(self):
        return self.checkbox


class URLPropertyValue(NotionPropertyValue):
    url: str

    @property
    def value(self):
        return self.url


class EmailPropertyValue(NotionPropertyValue):
    email: str

    @property
    def value(self):
        return self.email


class PhoneNumberPropertyValue(NotionPropertyValue):
    phone_number: str

    @property
    def value(self):
        return self.phone_number


class CreatedTimePropertyValue(NotionPropertyValue):
    created_time: str

    @property
    def value(self):
        return self.created_time


class CreatedByPropertyValue(NotionPropertyValue):
    created_by: UserObject

    @property
    def value(self):
        return self.created_by.name


class LastEditedTimePropertyValue(NotionPropertyValue):
    last_edited_time: str

    @property
    def value(self):
        return self.last_edited_time


class LastEditedByPropertyValue(NotionPropertyValue):
    last_edited_by: UserObject

    @property
    def value(self):
        return self.last_edited_by.name
