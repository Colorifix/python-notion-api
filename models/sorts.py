from typing import Literal, Optional

from pydantic import BaseModel, Field, root_validator

from notion_integration.api.models.fields import propertyField


class Sort(BaseModel):
    sort_property: str = propertyField
    direction: Literal["ascending", "descending"]
    descending: Optional[bool] = Field(export=False, default=False)

    @root_validator(pre=True)
    def validate_values(cls, values):
        values['direction'] = (
            "descending" if 'descending' in values else "ascending"
        )
        return values
