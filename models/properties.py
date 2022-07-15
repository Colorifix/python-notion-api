from typing import Optional, List, Dict

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
    StatusObject,
    FileReferenceObject,
    NotionObject,
    Pagination
)


class PropertyItemPagination(Pagination):
    property_item: Dict

    _class_map = {
        "rich_text": "RichTextPagination",
        "title": "TitlePagination",
        "people": "PeoplePagination",
        "relationships": "RelationshipsPagination"
    }

    @property
    def _class_key_field(self):
        return self.property_item['type']


class PropertyItem(NotionObject):
    property_id: str = idField
    propety_type: Optional[str] = typeField
    next_url: Optional[str]

    _class_map = {
        "number": "NumberProperty",
        "select": "SelectProperty",
        "multi_select": "MultiSelectProperty",
        "status": "StatusProperty",
        "date": "DateProperty",
        "formula": "FormulaProperty",
        "rollup": "RollupProperty",
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

    @property
    def _class_key_field(self):
        return self.propety_type


class TitlePropertyItem(PropertyItem):
    _class_key_field = None

    title: List[RichTextObject]

    @property
    def value(self):
        return "".join([rto.plain_text for rto in self.title])


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

    number: float

    @property
    def value(self):
        return self.number


class SelectPropertyItem(PropertyItem):
    _class_key_field = None

    select: SelectObject

    @property
    def value(self):
        return self.select.name


class StatusPropertyItem(PropertyItem):
    _class_key_field = None

    status: StatusObject

    @property
    def value(self):
        return self.status.name


class MultiSelectPropertyItem(PropertyItem):
    _class_key_field = None

    multi_select: List[SelectObject]

    @property
    def value(self):
        return [so.name for so in self.multi_select]


class DatePropertyItem(PropertyItem):
    _class_key_field = None

    date: DatePropertyValueObject

    @property
    def value(self):
        return self.date.start


class FormulaPropertyItem(PropertyItem):
    _class_key_field = None

    formula: FormulaObject

    @property
    def value(self):
        return ''


class RelationPropertyItem(PropertyItem):
    _class_key_field = None

    relation: PageReferenceObject

    @property
    def value(self):
        return [pr.page_id for pr in self.relation]


class RelationPagination(PropertyItemPagination):
    _class_key_field = None

    results: List[RelationPropertyItem]


class RollupPropertyItem(PropertyItem):
    _class_key_field = None

    rollup: RollupObject

    @property
    def value(self):
        return ''


class PeoplePropertyItem(PropertyItem):
    _class_key_field = None

    people: UserObject

    @property
    def value(self):
        return [p.name for p in self.people]


class PeoplePagination(PropertyItemPagination):
    _class_key_field = None

    results: List[RelationPropertyItem]


class FilesPropertyItem(PropertyItem):
    _class_key_field = None

    files: List[FileReferenceObject]

    @property
    def value(self):
        return [file.value for file in self.files] 


class CheckBoxPropertyItem(PropertyItem):
    _class_key_field = None

    checkbox: bool

    @property
    def value(self):
        return self.checkbox


class URLPropertyItem(PropertyItem):
    _class_key_field = None

    url: str

    @property
    def value(self):
        return self.url


class EmailPropertyItem(PropertyItem):
    _class_key_field = None

    email: str

    @property
    def value(self):
        return self.email


class PhoneNumberPropertyItem(PropertyItem):
    _class_key_field = None

    phone_number: str

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

    created_by: UserObject

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

    last_edited_by: UserObject

    @property
    def value(self):
        return self.last_edited_by.name
