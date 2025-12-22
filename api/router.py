# app/api/router.py
from fastapi import APIRouter

from .datasets import router as datasets_router


api_router = APIRouter(prefix="/api")

api_router.include_router(datasets_router, tags=["datasets"])
