from pydantic import BaseModel, Extra
from typing import Optional, Literal, List

from notion_integration.api.models.fields import (
    idField, typeField
)

from notion_integration.api.models.objects import (
    UserObject,
    DatePropertyValueObject,
    RichTextObject,
    SelectObject,
    FormulaObject,
    PageReferenceObject,
    RollupObject,
    FileObject,
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


class NotionProperty(BaseModel, extra=Extra.allow):
    property_id: str = idField
    propety_type: Optional[str] = typeField

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
            cls for cls in NotionProperty.__subclasses__()
            if cls.__name__ == cls_name
        ), None)


class TitleProperty(NotionProperty):
    title: List[RichTextObject]

    @property
    def value(self):
        return "".join([rto.plain_text for rto in self.title])


class RichTextProperty(NotionProperty):
    rich_text: List[RichTextObject]

    @property
    def value(self):
        return "".join([rto.plain_text for rto in self.rich_text])


class NumberProperty(NotionProperty):
    number: float

    @property
    def value(self):
        return self.number


class SelectProperty(NotionProperty):
    select: SelectObject

    @property
    def value(self):
        return self.select.name


class StatusProperty(NotionProperty):
    status: StatusObject

    @property
    def value(self):
        return self.status.name


class MultiSelectProperty(NotionProperty):
    multi_select: List[SelectObject]

    @property
    def value(self):
        return [so.name for so in self.multi_select]


class DateProperty(NotionProperty):
    date: DatePropertyValueObject

    @property
    def value(self):
        return self.date.start


class FormulaProperty(NotionProperty):
    formula: FormulaObject

    @property
    def value(self):
        return ''


class RelationProperty(NotionProperty):
    relation: List[PageReferenceObject]

    @property
    def value(self):
        return [pr.page_id for pr in self.relation]


class RollupProperty(NotionProperty):
    rollup: RollupObject

    @property
    def value(self):
        return ''


class PeopleProperty(NotionProperty):
    people: List[UserObject]

    @property
    def value(self):
        return [p.name for p in self.people]


class FilesProperty(NotionProperty):
    files: List[FileReferenceObject]

    @property
    def value(self):
        return [file.value for file in self.files] 


class CheckBoxProperty(NotionProperty):
    checkbox: bool

    @property
    def value(self):
        return self.checkbox


class URLProperty(NotionProperty):
    url: str

    @property
    def value(self):
        return self.url


class EmailProperty(NotionProperty):
    email: str

    @property
    def value(self):
        return self.email


class PhoneNumberProperty(NotionProperty):
    phone_number: str

    @property
    def value(self):
        return self.phone_number


class CreatedTimeProperty(NotionProperty):
    created_time: str

    @property
    def value(self):
        return self.created_time


class CreatedByProperty(NotionProperty):
    created_by: UserObject

    @property
    def value(self):
        return self.created_by.name


class LastEditedTimeProperty(NotionProperty):
    last_edited_time: str

    @property
    def value(self):
        return self.last_edited_time


class LastEditedByProperty(NotionProperty):
    last_edited_by: UserObject

    @property
    def value(self):
        return self.last_edited_by.name
