import os
from typing import List
import uuid
import base64
import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
import mne

from models.dataset import DatasetFileMetadata, DatasetMetadata


router = APIRouter()

DATASETS_DIR = Path("datasets")
DATASETS_DIR.mkdir(exist_ok=True)

def generate_artifact_id(length: int = 8) -> str:
    raw = uuid.uuid4().bytes
    b32 = base64.b32encode(raw).decode("ascii").lower()
    return b32[:length]


def get_meta_path(file_id: str) -> Path:
    return DATASETS_DIR / (file_id + ".meta")


def save_metadata(file_id: str, metadata: dict):
    meta_path = get_meta_path(file_id)
    with open(meta_path, "w") as f:
        json.dump(metadata, f)


def load_metadata(file_id: str) -> dict:
    meta_path = get_meta_path(file_id)
    if meta_path.exists():
        with open(meta_path, "r") as f:
            return json.load(f)
    return {}


def save_raw(raw: mne.io.BaseRaw):
    file_id = str(generate_artifact_id())
    file_path = DATASETS_DIR / (file_id + ".fif")
    raw.save(file_path, overwrite=True)
    return file_id

def get_raw_from_id(id: str) -> mne.io.BaseRaw:
    file_path = DATASETS_DIR / (id + ".fif")
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # raw = mne.io.read_raw_edf(file_path, preload=False)
    raw = mne.io.read_raw_fif(file_path, preload=True)
    return raw


@router.post("/datasets/new")
async def upload_dataset(file: UploadFile = File(...)):
    # Validate file extension
    if not file.filename or not file.filename.lower().endswith('.edf'):
        raise HTTPException(status_code=400, detail="Only .EDF files are accepted")

    file_path = DATASETS_DIR / (generate_artifact_id() + ".edf")
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    raw = mne.io.read_raw_edf(file_path, preload=False)
    fif_file_id = save_raw(raw)

    save_metadata(fif_file_id, {"original_filename": file.filename})

    return {"id": fif_file_id}


@router.get("/datasets/{id}", response_class=FileResponse)
async def get_dataset(id: str):
    
    raw = get_raw_from_id(id)
    file_path = DATASETS_DIR / (id + ".edf")
    
    raw.export(file_path, fmt="edf", overwrite=True)

    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Dataset not found")

    
    return FileResponse(file_path, filename=f"{id}.edf")


@router.get("/datasets/{id}/metadata", response_model=DatasetMetadata)
async def get_dataset_metadata(id: str):

    raw = get_raw_from_id(id)

    info = raw.info

    duration_sec = raw.times[-1] if raw.n_times > 0 else 0.0
    eeg_channel_count = sum(
        ch_type == "eeg" for ch_type in raw.get_channel_types()
    )

    meta = load_metadata(id)
    original_filename = meta.get("original_filename", f"{id}.edf")

    return DatasetMetadata(
        original_filename=original_filename,
        duration_seconds=duration_sec,
        sampling_frequency_hz=info["sfreq"],
        time_points=raw.n_times,
        eeg_channel_count=eeg_channel_count,
        highpass_hz=info.get("highpass", 0.0),
        lowpass_hz=info.get("lowpass", 0.0),
    )

@router.get("/datasets", response_model=List[DatasetFileMetadata])
async def list_datasets():
    datasets = []
    for file in DATASETS_DIR.glob("*.fif"):
        meta = load_metadata(file.stem)
        original_filename = meta.get("original_filename", file.name)
        datasets.append({
            "id": file.stem,
            "original_filename": original_filename,
            "size_bytes": file.stat().st_size,
            "created_at": file.stat().st_ctime,
            "modified_at": file.stat().st_mtime,
        })
    return datasets

@router.delete("/datasets/{id}")
async def delete_dataset(id: str):
    file_path = DATASETS_DIR / (id + ".fif")
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    os.remove(file_path)
    
    # Remove metadata file if it exists
    meta_path = get_meta_path(id)
    if meta_path.exists():
        os.remove(meta_path)
    
    return {"message": "Dataset deleted", "id": id}