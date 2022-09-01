class Filter:
    def __init__(self, property_name, **kwargs):
        self.property_name = property_name
        self.kwargs = kwargs

    def to_dict(self, type_name):
        return {
            "property": self.property_name,
            type_name: self.kwargs
        }


class AndFilter:
    def __init__(self, filters: List[Union[Filter, AndFilter]]):
        self.filters = filters

    def to_dict(self):



db.query(
    filter=Filter(
        "Select",
        is_equal="foo"
    )
)

db.query(
    filter=AndFilter([
        Filter(

        )
    ])
)

# import re

# from typing import Optional, Dict, Literal, Union, List, ClassVar, Type

# from pydantic import BaseModel, Field

# from notion_integration.api.models.fields import (
#         propertyField, filterField, andField, orField
# )


# class DateFilterCondition(BaseModel):
#     equals: Optional[str]
#     before: Optional[str]
#     after: Optional[str]
#     on_or_before: Optional[str]
#     is_empty: Optional[Literal[True]]
#     is_not_empty: Optional[Literal[True]]
#     on_or_after: Optional[str]
#     past_week: Optional[Dict]
#     past_month: Optional[Dict]
#     past_year: Optional[Dict]
#     next_week: Optional[Dict]
#     next_month: Optional[Dict]
#     next_year: Optional[Dict]


# class TextFilterCondition(BaseModel):
#     equals: Optional[str]
#     does_not_equal: Optional[str]
#     contains: Optional[str]
#     does_not_contain: Optional[str]
#     starts_with: Optional[str]
#     ends_with: Optional[str]
#     is_empty: Optional[Literal[True]]
#     is_not_empty: Optional[Literal[True]]


# class NumberFilterCondition(BaseModel):
#     equals: Optional[int]
#     does_not_equal: Optional[int]
#     greater_than: Optional[int]
#     less_than: Optional[int]
#     greater_than_or_equal_to: Optional[int]
#     less_than_or_equal_to: Optional[int]
#     is_empty: Optional[Literal[True]]
#     is_not_empty: Optional[Literal[True]]


# class CheckboxFilterCondition(BaseModel):
#     equals: Optional[bool]
#     does_not_equal: Optional[bool]


# class SelectFilterCondition(BaseModel):
#     equals: Optional[str]
#     does_not_equal: Optional[str]
#     is_empty: Optional[Literal[True]]
#     is_not_empty: Optional[Literal[True]]


# class MultiSelectPropertyCondition(BaseModel):
#     contains: Optional[str]
#     does_not_contain: Optional[str]
#     is_empty: Optional[Literal[True]]
#     is_not_empty: Optional[Literal[True]]


# class PeopleFilterCondition(BaseModel):
#     contains: Optional[str]
#     does_not_contain: Optional[str]
#     is_empty: Optional[Literal[True]]
#     is_not_empty: Optional[Literal[True]]


# class RelationFilterCondition(BaseModel):
#     contains: Optional[str]
#     does_not_contain: Optional[str]
#     is_empty: Optional[Literal[True]]
#     is_not_empty: Optional[Literal[True]]


# class FilesFilterCondition(BaseModel):
#     is_empty: Optional[Literal[True]]
#     is_not_empty: Optional[Literal[True]]


# class FormulaFilterCondition(BaseModel):
#     string: Optional[TextFilterCondition]
#     checkbox: Optional[CheckboxFilterCondition]
#     number: Optional[NumberFilterCondition]
#     date: Optional[DateFilterCondition]


# class DictGetter(GetterDict):
#     def get(self, key: str, default: Any) -> Any:


# class PropertyFilter(BaseModel):
#     _filter_field: ClassVar[str]
#     filter_property: str = propertyField



#     class Config:
#         orm_mode = True
#         getter_dict = UserGetter


# class RichTextFilter(PropertyFilter):
#     rich_text: TextFilterCondition


# class PhoneNumberFilter(PropertyFilter):
#     phone_number: TextFilterCondition


# class NumberFilter(PropertyFilter):
#     number: NumberFilterCondition


# class CheckboxFilter(PropertyFilter):
#     checkbox: CheckboxFilterCondition


# class SelectFilter(PropertyFilter):
#     select: SelectFilterCondition


# class MultiSelectFilter(PropertyFilter):
#     multi_select = Field(alias='multi-select')


# class DateFilter(PropertyFilter):
#     date: DateFilterCondition


# class PeopleFiter(PropertyFilter):
#     people: PeopleFilterCondition


# class FilesFilter(PropertyFilter):
#     files: FilesFilterCondition


# class RelationFilter(PropertyFilter):
#     relation: RelationFilterCondition


# class FormulaFilter(PropertyFilter):
#     formula: FormulaFilterCondition


# class TimestampFilter(BaseModel):
#     timestamp: DateFilterCondition


# FilterItem = Union[
#     PropertyFilter,
#     TimestampFilter,
#     "AndFilter",
#     "OrFilter"
# ]


# class AndFilter(BaseModel):
#     filter_and: List[FilterItem] = andField


# class OrFilter(BaseModel):
#     filter_or: List[FilterItem] = orField


# class Filter(BaseModel):
#     filter_filter: FilterItem = filterField

# class F(BaseModel):


# # def property_filter(filter_type: Type[PropertyFilter], **kwargs):
# #     pattern = re.compile(r'(?<!^)(?=[A-Z])')
# #     field_name = pattern.sub('_', filter_type.__name__).lower().replace(
# #         '_filter', ''
# #     )

# #     return Filter(filter=filter_type(**{field_name: kwargs}))
