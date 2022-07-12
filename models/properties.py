from pydantic import BaseModel, Extra, ValidationError
from typing import Optional, Literal, List, Dict, ClassVar, Callable

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


def get_derived_class(self, base_class, derived_cass_name):
    return next((
        cls for cls in base_class.__subclasses__()
        if cls.__name__ == derived_cass_name
    ), None)


class NotionObjectBase(BaseModel):
    _class_map: Optional[ClassVar[Dict[str, str]]]

    @classmethod
    def from_obj(cls, obj):
        temp_obj = cls(obj)
        class_key_value = temp_obj._class_key_field
        if class_key_value is None:
            raise ValueError(
                f"Given object does not have a {cls._class_key_field} field"
            )

        class_name = cls._class_map.get(class_key_value, None)
        if class_name is None:
            raise ValueError(
                f"Unknown object {cls._class_key_field}: '{class_key_value}'"
            )

        derived_cls = get_derived_class(cls, class_name)

        if derived_cls._class_key_field is not None:
            return derived_cls.from_obj(obj)


class NotionObject(NotionObjectBase, extra=Extra.allow):
    notion_object: str = objectField

    _class_map = {
        "list": "Pagination",
        "property_item": "PropetyItem"
    }

    @property
    def _class_key_field(self):
        return self.notion_object


class Pagination(NotionObject):
    has_more: bool
    next_cursor: str
    results: List
    pagination_type: Literal[
        "block", "page", "user", "database", "property_item",
        "page_or_database"
    ] = typeField

    _class_map = {
        "property_item": "PropertyItemPagination"
    }

    @property
    def _class_key_field(self):
        return self.pagination_type


class PropertyItemPagination(Pagination):
    pagination_item: Dict

    _class_map = {
        "rich_text": "RichTextPagination",
        "title": "TitlePagination",
        "people": "PeoplePagination",
        "relationships": "RelationshipsPagination"
    }

    @property
    def _class_key_field(self):
        return self.pagination_item['type']


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
    title: List[RichTextObject]

    @property
    def value(self):
        return "".join([rto.plain_text for rto in self.title])


class TitlePagination(PropertyItemPagination):
    results: List[TitlePropertyItem]


class RichTextPropertyItem(PropertyItem):
    rich_text: RichTextObject

    @property
    def value(self):
        return "".join([rto.plain_text for rto in self.rich_text])


class RichTextPagination(PropertyItemPagination):
    results: List[RichTextPropertyItem]


class NumberPropertyItem(PropertyItem):
    number: float

    @property
    def value(self):
        return self.number


class SelectPropertyItem(PropertyItem):
    select: SelectObject

    @property
    def value(self):
        return self.select.name


class StatusPropertyItem(PropertyItem):
    status: StatusObject

    @property
    def value(self):
        return self.status.name


class MultiSelectPropertyItem(PropertyItem):
    multi_select: List[SelectObject]

    @property
    def value(self):
        return [so.name for so in self.multi_select]


class DatePropertyItem(PropertyItem):
    date: DatePropertyValueObject

    @property
    def value(self):
        return self.date.start


class FormulaPropertyItem(PropertyItem):
    formula: FormulaObject

    @property
    def value(self):
        return ''


class RelationPropertyItem(PropertyItem):
    relation: PageReferenceObject

    @property
    def value(self):
        return [pr.page_id for pr in self.relation]


class RelationPagination(PropertyItemPagination):
    results: List[RelationPropertyItem]


class RollupPropertyItem(PropertyItem):
    rollup: RollupObject

    @property
    def value(self):
        return ''


class PeoplePropertyItem(PropertyItem):
    people: UserObject

    @property
    def value(self):
        return [p.name for p in self.people]


class PeoplePagination(PropertyItemPagination):
    results: List[RelationPropertyItem]


class FilesPropertyItem(PropertyItem):
    files: List[FileReferenceObject]

    @property
    def value(self):
        return [file.value for file in self.files] 


class CheckBoxPropertyItem(PropertyItem):
    checkbox: bool

    @property
    def value(self):
        return self.checkbox


class URLPropertyItem(PropertyItem):
    url: str

    @property
    def value(self):
        return self.url


class EmailPropertyItem(PropertyItem):
    email: str

    @property
    def value(self):
        return self.email


class PhoneNumberPropertyItem(PropertyItem):
    phone_number: str

    @property
    def value(self):
        return self.phone_number


class CreatedTimePropertyItem(PropertyItem):
    created_time: str

    @property
    def value(self):
        return self.created_time


class CreatedByPropertyItem(PropertyItem):
    created_by: UserObject

    @property
    def value(self):
        return self.created_by.name


class LastEditedTimePropertyItem(PropertyItem):
    last_edited_time: str

    @property
    def value(self):
        return self.last_edited_time


class LastEditedByPropertyItem(PropertyItem):
    last_edited_by: UserObject

    @property
    def value(self):
        return self.last_edited_by.name
