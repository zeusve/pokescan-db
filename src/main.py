"""FastAPI application entry point — router registration only."""

from fastapi import FastAPI

from . import security, vision
from .routers import collection

app = FastAPI(title="PokeScan DB", version="0.1.0")

app.include_router(security.router)
app.include_router(vision.router)
app.include_router(collection.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
