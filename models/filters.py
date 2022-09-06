import re

from typing import Optional, Dict, Literal, Union, List

from pydantic import BaseModel, Extra, root_validator

from notion_integration.api.models.fields import (
        propertyField, andField, orField
)


class DateFilterCondition(BaseModel):
    equals: Optional[str]
    before: Optional[str]
    after: Optional[str]
    on_or_before: Optional[str]
    is_empty: Optional[Literal[True]]
    is_not_empty: Optional[Literal[True]]
    on_or_after: Optional[str]
    past_week: Optional[Dict]
    past_month: Optional[Dict]
    past_year: Optional[Dict]
    next_week: Optional[Dict]
    next_month: Optional[Dict]
    next_year: Optional[Dict]


class TextFilterCondition(BaseModel):
    equals: Optional[str]
    does_not_equal: Optional[str]
    contains: Optional[str]
    does_not_contain: Optional[str]
    starts_with: Optional[str]
    ends_with: Optional[str]
    is_empty: Optional[Literal[True]]
    is_not_empty: Optional[Literal[True]]


class NumberFilterCondition(BaseModel):
    equals: Optional[int]
    does_not_equal: Optional[int]
    greater_than: Optional[int]
    less_than: Optional[int]
    greater_than_or_equal_to: Optional[int]
    less_than_or_equal_to: Optional[int]
    is_empty: Optional[Literal[True]]
    is_not_empty: Optional[Literal[True]]


class CheckboxFilterCondition(BaseModel):
    equals: Optional[bool]
    does_not_equal: Optional[bool]


class SelectFilterCondition(BaseModel):
    equals: Optional[str]
    does_not_equal: Optional[str]
    is_empty: Optional[Literal[True]]
    is_not_empty: Optional[Literal[True]]


class MultiSelectFilterCondition(BaseModel):
    contains: Optional[str]
    does_not_contain: Optional[str]
    is_empty: Optional[Literal[True]]
    is_not_empty: Optional[Literal[True]]


class PeopleFilterCondition(BaseModel):
    contains: Optional[str]
    does_not_contain: Optional[str]
    is_empty: Optional[Literal[True]]
    is_not_empty: Optional[Literal[True]]


class RelationFilterCondition(BaseModel):
    contains: Optional[str]
    does_not_contain: Optional[str]
    is_empty: Optional[Literal[True]]
    is_not_empty: Optional[Literal[True]]


class FilesFilterCondition(BaseModel):
    is_empty: Optional[Literal[True]]
    is_not_empty: Optional[Literal[True]]


class FormulaFilterCondition(BaseModel):
    string: Optional[TextFilterCondition]
    checkbox: Optional[CheckboxFilterCondition]
    number: Optional[NumberFilterCondition]
    date: Optional[DateFilterCondition]


class PropertyFilter(BaseModel, extra=Extra.ignore):
    filter_property: str = propertyField

    @root_validator(pre=True)
    def validate_values(cls, values):
        pattern = re.compile(r'(?<!^)(?=[A-Z])')
        field_name = pattern.sub('_', cls.__name__).lower().replace(
            '_filter', ''
        )
        values[field_name] = values
        return values


class RichTextFilter(PropertyFilter):
    rich_text: TextFilterCondition


class PhoneNumberFilter(PropertyFilter):
    phone_number: TextFilterCondition


class NumberFilter(PropertyFilter):
    number: NumberFilterCondition


class CheckboxFilter(PropertyFilter):
    checkbox: CheckboxFilterCondition


class SelectFilter(PropertyFilter):
    select: SelectFilterCondition


class MultiSelectFilter(PropertyFilter):
    multi_select: MultiSelectFilterCondition


class DateFilter(PropertyFilter):
    date: DateFilterCondition


class PeopleFiter(PropertyFilter):
    people: PeopleFilterCondition


class FilesFilter(PropertyFilter):
    files: FilesFilterCondition


class RelationFilter(PropertyFilter):
    relation: RelationFilterCondition


class FormulaFilter(PropertyFilter):
    formula: FormulaFilterCondition


class TimestampFilter(BaseModel):
    timestamp: DateFilterCondition


FilterItem = Union[
    PropertyFilter,
    TimestampFilter,
    "AndFilter",
    "OrFilter"
]


class AndFilter(BaseModel):
    filter_and: List[FilterItem] = andField


class OrFilter(BaseModel):
    filter_or: List[FilterItem] = orField


def or_filter(filters: List[FilterItem]):
    return OrFilter(**{"or": filters})


def and_filter(filters: List[FilterItem]):
    return AndFilter(**{"and": filters})


AndFilter.update_forward_refs()
OrFilter.update_forward_refs()
