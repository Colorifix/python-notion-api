from typing import List, Optional

from pydantic import BaseModel, Field, PositiveInt


class RetryStrategy(BaseModel):
    total: PositiveInt
    backoff_factor: Optional[float] = Field(0, gte=0)
    max_backoff: Optional[float] = Field(5, gte=0)
    status_forcelist: List[int]
