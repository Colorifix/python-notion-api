import re
from typing import Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Extra, StrictFloat, StrictInt, root_validator

from python_notion_api.models.fields import andField, orField, propertyField


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
    equals: Optional[Union[StrictInt, StrictFloat]]
    does_not_equal: Optional[Union[StrictInt, StrictFloat]]
    greater_than: Optional[Union[StrictInt, StrictFloat]]
    less_than: Optional[Union[StrictInt, StrictFloat]]
    greater_than_or_equal_to: Optional[Union[StrictInt, StrictFloat]]
    less_than_or_equal_to: Optional[Union[StrictInt, StrictFloat]]
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


class StatusFilterCondition(BaseModel):
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


class RollupFilterCondition(BaseModel):
    any: Optional["PropertyFilter"]
    every: Optional["PropertyFilter"]
    none: Optional["PropertyFilter"]
    number: Optional[NumberFilterCondition]
    date: Optional[DateFilterCondition]


class BaseFilter(BaseModel, extra=Extra.ignore):
    @root_validator(pre=True)
    def validate_values(cls, values):
        pattern = re.compile(r"(?<!^)(?=[A-Z])")
        field_name = (
            pattern.sub("_", cls.__name__).lower().replace("_filter", "")
        )
        values[field_name] = values
        return values


class PropertyFilter(BaseFilter):
    filter_property: Optional[str] = propertyField


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


class StatusFilter(PropertyFilter):
    status: StatusFilterCondition


class MultiSelectFilter(PropertyFilter):
    multi_select: MultiSelectFilterCondition


class DateFilter(PropertyFilter):
    date: DateFilterCondition


class PeopleFilter(PropertyFilter):
    people: PeopleFilterCondition


class FilesFilter(PropertyFilter):
    files: FilesFilterCondition


class RelationFilter(PropertyFilter):
    relation: RelationFilterCondition


class FormulaFilter(PropertyFilter):
    formula: FormulaFilterCondition


class RollupFilter(PropertyFilter):
    rollup: RollupFilterCondition


class TimestampFilter(BaseFilter):
    timestamp: str


class CreatedTimeFilter(TimestampFilter):
    created_time: DateFilterCondition


class LastEditedTimeFilter(TimestampFilter):
    last_edited_time: DateFilterCondition


FilterItem = Union[PropertyFilter, TimestampFilter, "AndFilter", "OrFilter"]


class AndFilter(BaseModel):
    filter_and: List[FilterItem] = andField


class OrFilter(BaseModel):
    filter_or: List[FilterItem] = orField


def or_filter(filters: List[FilterItem]):
    """
    Combine filters with an OR condition.
    Notion limits the number of items in an OR filter to 100.
    If there are more than 100 items, we split into smaller ORfilters and
    then join them in an ORFilter.
    Notion limits the nesting to two-levels. If that changes, can use
    'while' instead of 'if'
    Args:
        filters:

    Returns:

    """
    if len(filters) > 100:
        filters = [
            or_filter(filters[i : i + 100])
            for i in range(0, len(filters), 100)
        ]
    return OrFilter(**{"or": filters})


def and_filter(filters: List[FilterItem]):
    """
    Combine filters with an AND condition.
    Notion limits the number of items in an AND filter to 100.
    If there are more than 100 items, we split into smaller ANDFilters and
    then join them in an AND_filter.
    Notion limits the nesting to two-levels. If that changes, can use
    'while' instead of 'if'
    Args:
        filters:

    Returns:

    """
    if len(filters) > 100:
        filters = [
            and_filter(filters[i : i + 100])
            for i in range(0, len(filters), 100)
        ]
    return AndFilter(**{"and": filters})


RollupFilterCondition.update_forward_refs()
AndFilter.update_forward_refs()
OrFilter.update_forward_refs()
