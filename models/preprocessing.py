from pydantic import BaseModel
from typing import Optional, Literal


class GetChannelsResponse(BaseModel):
    channels: list[str]


class PickChannelsRequest(BaseModel):
    mode: Literal["manual", "all_eeg"]
    channels: Optional[list[str]] = None  # Required when mode is "manual"


class BaseResponse(BaseModel):
    id: str


class PickChannelsResponse(BaseModel):
    id: str
    channels: list[str]

