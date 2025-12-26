from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import matplotlib
matplotlib.use("Agg")  # Use non-interactive backend for saving figures
import matplotlib.pyplot as plt

from api.datasets import get_raw_from_id


router = APIRouter()

VISUALS_DIR = Path("visuals")
VISUALS_DIR.mkdir(exist_ok=True)


def get_visual_path(id: str, visual_type: str) -> Path:
    """Get the path for a cached visualization."""
    return VISUALS_DIR / f"{id}_{visual_type}.png"


@router.get("/datasets/{id}/visualizations/plot", response_class=FileResponse)
async def get_raw_plot(id: str):
    """Generate and return a raw EEG plot visualization."""
    visual_path = get_visual_path(id, "plot")
    
    # Return cached version if it exists
    if visual_path.exists():
        return FileResponse(visual_path, media_type="image/png", filename=f"{id}_plot.png")
    
    # Generate the visualization
    raw = get_raw_from_id(id)
    raw.load_data()
    
    fig = raw.plot(show=False)
    fig.savefig(visual_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    
    return FileResponse(visual_path, media_type="image/png", filename=f"{id}_plot.png")


@router.get("/datasets/{id}/visualizations/psd", response_class=FileResponse)
async def get_psd_plot(id: str):
    """Generate and return a PSD (Power Spectral Density) plot visualization."""
    visual_path = get_visual_path(id, "psd_plot")
    
    # Return cached version if it exists
    if visual_path.exists():
        return FileResponse(visual_path, media_type="image/png", filename=f"{id}_psd_plot.png")
    
    # Generate the visualization
    raw = get_raw_from_id(id)
    raw.load_data()
    
    fig = raw.compute_psd().plot(show=False)
    fig.savefig(visual_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    
    return FileResponse(visual_path, media_type="image/png", filename=f"{id}_psd_plot.png")


@router.get("/datasets/{id}/visualizations/psd_topomap", response_class=FileResponse)
async def get_psd_topomap(id: str):
    """Generate and return a PSD topomap visualization."""
    visual_path = get_visual_path(id, "psd_topomap")
    
    # Return cached version if it exists
    if visual_path.exists():
        return FileResponse(visual_path, media_type="image/png", filename=f"{id}_psd_topomap.png")
    
    # Generate the visualization
    raw = get_raw_from_id(id)
    raw.load_data()
    
    # Check if montage is set, required for topomap
    if raw.get_montage() is None:
        raise HTTPException(
            status_code=400, 
            detail="Dataset does not have a montage set. Topomap requires electrode positions."
        )
    
    fig = raw.compute_psd().plot_topomap(show=False)
    fig.savefig(visual_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    
    return FileResponse(visual_path, media_type="image/png", filename=f"{id}_psd_topomap.png")
