# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
import typing
from ..core.pydantic_utilities import IS_PYDANTIC_V2
import pydantic


class EvaluatorConfig(UniversalBaseModel):
    id: str
    name: str
    project_id: str
    evaluator_key: str
    settings_values: typing.Optional[
        typing.Dict[str, typing.Optional[typing.Any]]
    ] = None
    created_at: str
    updated_at: str

    if IS_PYDANTIC_V2:
        model_config: typing.ClassVar[pydantic.ConfigDict] = pydantic.ConfigDict(
            extra="allow", frozen=True
        )  # type: ignore # Pydantic v2
    else:

        class Config:
            frozen = True
            smart_union = True
            extra = pydantic.Extra.allow
