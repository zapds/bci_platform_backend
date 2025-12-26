from fastapi import APIRouter, HTTPException
import mne

from models.preprocessing import BaseResponse, GetChannelsResponse, PickChannelsRequest, PickChannelsResponse
from .datasets import get_raw_from_id, save_raw


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
