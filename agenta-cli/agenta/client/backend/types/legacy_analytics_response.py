# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
import typing
from .legacy_data_point import LegacyDataPoint
from ..core.pydantic_utilities import IS_PYDANTIC_V2
import pydantic


class LegacyAnalyticsResponse(UniversalBaseModel):
    total_count: int
    failure_rate: float
    total_cost: float
    avg_cost: float
    avg_latency: float
    total_tokens: int
    avg_tokens: float
    data: typing.List[LegacyDataPoint]

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(
            extra="allow", frozen=True
        )  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow
