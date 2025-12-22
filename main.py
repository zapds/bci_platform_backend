from fastapi import FastAPI
from api.router import api_router

app = FastAPI(
    title="BCI Platform Backend",
)

app.include_router(api_router)


