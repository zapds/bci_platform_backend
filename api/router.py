# app/api/router.py
from fastapi import APIRouter

from .datasets import router as datasets_router
from .preprocessing import router as preprocessing_router
from .visualizations import router as visualizations_router


api_router = APIRouter(prefix="/api")

api_router.include_router(datasets_router, tags=["datasets"])
api_router.include_router(preprocessing_router, tags=["preprocessing"])
api_router.include_router(visualizations_router, tags=["visualizations"])
