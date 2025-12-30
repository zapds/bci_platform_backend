from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
import mne
import pandas as pd

from models.preprocessing import BaseResponse, GetChannelsResponse, PickChannelsRequest, PickChannelsResponse, SetAnnotationsRequest
from .datasets import get_raw_from_id, save_raw, DATASETS_DIR


router = APIRouter()

EEG_CHANNELS = [
    
]

@router.get("/preprocessing/{id}/channels", response_model=GetChannelsResponse)
async def list_channels(id: str):
    raw = get_raw_from_id(id)
    return {"channels": raw.info["ch_names"]}


@router.post("/preprocessing/{id}/pick_channels", response_model=PickChannelsResponse)
async def pick_channels(id: str, request: PickChannelsRequest):
    raw = get_raw_from_id(id)
    raw.load_data()

    if request.mode == "manual":
        if not request.channels:
            raise HTTPException(status_code=400, detail="Channels list is required for manual mode")
        
        # Validate that all requested channels exist
        invalid_channels = [ch for ch in request.channels if ch not in raw.info["ch_names"]]
        if invalid_channels:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid channel names: {invalid_channels}"
            )
        
        raw.pick_channels(request.channels)
    
    elif request.mode == "all_eeg":
        # Pick only EEG channels
        eeg_channels = [
            ch_name for ch_name, ch_type in zip(raw.info["ch_names"], raw.get_channel_types())
            if ch_type == "eeg"
        ]
        
        if not eeg_channels:
            raise HTTPException(status_code=400, detail="No EEG channels found in dataset")
        
        raw.pick_channels(eeg_channels)

    # Save the modified raw to a new dataset
    new_id = save_raw(raw)

    return PickChannelsResponse(
        id=new_id,
        channels=raw.info["ch_names"]
    )

@router.post("/preprocessing/{id}/set_montage", response_model=BaseResponse)
async def set_montage(id: str, montage_name: str = "standard_1020") -> BaseResponse:
    raw = get_raw_from_id(id)
    raw.load_data()

    try:
        raw.set_montage(montage_name)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error setting montage: {str(e)}")

    new_id = save_raw(raw)

    return BaseResponse(id=new_id)

@router.post("/preprocessing/{id}/set_annotations", response_model=BaseResponse)
async def set_annotations(
    id: str,
    file: UploadFile = File(...),
    onset_column: str = Form(...),
    duration_column: str = Form(...),
    description_column: str = Form(...)
) -> BaseResponse:
    # Validate file type
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    # Save the CSV file
    csv_path = DATASETS_DIR / f"{id}_annotations.csv"
    content = await file.read()
    csv_path.write_bytes(content)
    
    # Read the CSV using pandas
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading CSV: {str(e)}")
    
    # Validate columns exist
    for col_name, col_value in [("onset_column", onset_column), ("duration_column", duration_column), ("description_column", description_column)]:
        if col_value not in df.columns:
            raise HTTPException(status_code=400, detail=f"Column '{col_value}' not found in CSV")
    
    # Extract columns as lists
    onsets = df[onset_column].tolist()
    durations = df[duration_column].tolist()
    descriptions = df[description_column].tolist()
    
    # Create MNE Annotations object
    annotations = mne.Annotations(onset=onsets, duration=durations, description=descriptions)
    
    # Load raw and set annotations
    raw = get_raw_from_id(id)
    raw.load_data()
    raw.set_annotations(annotations)
    
    # Save and return new ID
    new_id = save_raw(raw)
    
    return BaseResponse(id=new_id)
