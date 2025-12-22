from pydantic import BaseModel
from typing import Optional


class DatasetMetadata(BaseModel):
    original_filename: str
    duration_seconds: float
    sampling_frequency_hz: float
    time_points: int
    eeg_channel_count: int
    highpass_hz: float
    lowpass_hz: float


class DatasetResponse(BaseModel):
    dataset_id: str
    metadata: DatasetMetadata


class DatasetUploadResponse(BaseModel):
    id: str
    filename: Optional[str]


class DatasetFileMetadata(BaseModel):
    id: str
    original_filename: str
    size_bytes: int
    created_at: float
    modified_at: float


class DatasetDeleteResponse(BaseModel):
    message: str
    id: str
