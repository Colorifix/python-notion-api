from typing import Union, Optional

from datetime import datetime, date

from pydantic import BaseModel

from notion_integration.api.models.fields import (
    idField,
    typeField
)

from notion_integration.api.models.common import (
    FileObject
)


class FileReferenceValue(BaseModel):
    reference_type: str = typeField
    name: str
    external: Optional[FileObject]
    file: Optional[FileObject]

    @property
    def value(self):
        if self.external is not None:
            return self.external.url
        elif self.file is not None:
            return self.file.url


class DatePropertyValue(BaseModel):
    start: Union[datetime, date]
    end: Optional[Union[datetime, date]]
    time_zone: Optional[str]


class SelectValue(BaseModel):
    select_id: Optional[str] = idField
    name: str
    color: Optional[str]


class StatusValue(BaseModel):
    status_id: Optional[str] = idField
    name: str
    color: Optional[str]


class FormulaValue(BaseModel):
    formula_type: str = typeField


class PageReferenceValue(BaseModel):
    page_id: str = idField


class RollupValue(BaseModel):
    rollup_type: str = typeField
