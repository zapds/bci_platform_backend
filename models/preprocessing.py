from pydantic import BaseModel
from typing import Optional, Literal, Dict, List, Tuple


class GetChannelsResponse(BaseModel):
    channels: list[str]


class PickChannelsRequest(BaseModel):
    mode: Literal["manual", "all_eeg"]
    channels: Optional[list[str]] = None  # Required when mode is "manual"


class SetAnnotationsRequest(BaseModel):
    onset_column: str
    duration_column: str
    description_column: str

class FilterRequest(BaseModel):
    l_freq: float | None = None
    h_freq: float | None = None


class BaseResponse(BaseModel):
    id: str


class PickChannelsResponse(BaseModel):
    id: str
    channels: list[str]


class EpochsRequest(BaseModel):
    tmin: float
    tmax: float
    baseline: Tuple[float | None, float | None] | None = (None, 0)
    reject_criteria: Dict[str, float] | None = None
    events_filter: List[str] | None = None
    set_reference: bool = False

