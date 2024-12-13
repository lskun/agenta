# This file was auto-generated by Fern from our API Definition.

from ..core.pydantic_utilities import UniversalBaseModel
import typing
from ..core.pydantic_utilities import IS_PYDANTIC_V2
import pydantic


class HumanEvaluation(UniversalBaseModel):
    id: str
    app_id: str
    project_id: str
    evaluation_type: str
    variant_ids: typing.List[str]
    variant_names: typing.List[str]
    variants_revision_ids: typing.List[str]
    revisions: typing.List[str]
    testset_id: str
    testset_name: str
    status: str
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
