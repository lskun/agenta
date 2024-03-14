from enum import Enum
from datetime import datetime
from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field


class GenerationFilterParams(BaseModel):
    type: str = Field("generation")
    trace_id: Optional[str]
    environment: Optional[str]
    variant: Optional[str]


class ObservabilityDashboardDataRequestParams(BaseModel):
    timeRange: str = Field(default="24_hours")
    environment: Optional[str]
    variant: Optional[str]


class Error(BaseModel):
    message: str
    stacktrace: Optional[str] = None


class Status(str, Enum):
    INITIATED = "INITIATED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class SpanVariant(BaseModel):
    variant_id: str
    variant_name: str
    revision: int


class SpanStatus(BaseModel):
    value: Optional[Status]
    error: Optional[Error]


class Span(BaseModel):
    id: str
    created_at: datetime
    variant: SpanVariant
    environment: Optional[str]
    status: SpanStatus
    metadata: Dict[str, Any]
    user_id: str


class BaseSpan(BaseModel):
    parent_span_id: Optional[str]
    meta: Optional[Dict[str, Any]]
    event_name: str
    event_type: Optional[str]
    start_time: datetime = Field(default=datetime.now())
    duration: Optional[int]
    status: SpanStatus
    inputs: Optional[Dict[str, Any]]
    outputs: Optional[List[str]]
    prompt_system: Optional[str]
    prompt_user: Optional[str]
    tokens_input: Optional[int]
    tokens_output: Optional[int]
    token_total: Optional[int]
    cost: Optional[float]
    tags: Optional[List[str]]


class CreateSpan(BaseSpan):
    trace_id: str
    environment: Optional[str]


class LLMInputs(BaseModel):
    input_name: str
    input_value: str


class LLMContent(BaseModel):
    inputs: List[LLMInputs]
    output: str


class LLMModelParams(BaseModel):
    prompt: Dict[str, Any]
    params: Dict[str, Any]


class SpanDetail(Span):
    span_id: str
    content: LLMContent
    model_params: LLMModelParams


class Trace(Span):
    pass


class TraceDetail(Trace):
    pass


class ObservabilityData(BaseModel):
    timestamp: str
    success_count: int
    failure_count: int
    cost: float
    latency: float
    total_tokens: int
    prompt_tokens: int
    completion_tokens: int


class ObservabilityDashboardData(BaseModel):
    data: List[ObservabilityData]
    total_count: int
    failure_rate: float
    total_cost: float
    avg_cost: float
    avg_latency: float
    total_tokens: int
    avg_tokens: int


class CreateFeedback(BaseModel):
    feedback: Optional[str]
    score: Optional[float]
    meta: Optional[Dict]


class Feedback(CreateFeedback):
    feedback_id: str
    created_at: Optional[datetime]


class UpdateFeedback(BaseModel):
    feedback: str
    score: Optional[float]
    meta: Optional[Dict]


class BaseTrace(BaseModel):
    app_id: Optional[str]
    base_id: Optional[str]
    config_name: Optional[str]
    cost: Optional[float]
    status: str = Field(default=Status.INITIATED)
    token_consumption: Optional[int]
    tags: Optional[List[str]]
    start_time: datetime = Field(default=datetime.now())


class CreateTrace(BaseTrace):
    environment: Optional[str]


class UpdateTrace(BaseModel):
    status: str
    end_time: datetime
