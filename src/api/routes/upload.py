"""File upload endpoints."""

from __future__ import annotations

from fastapi import APIRouter, UploadFile, File

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/")
async def upload(file: UploadFile = File(...)) -> dict:
    # Placeholder: store file and kick off ingestion later.
    return {"filename": file.filename, "content_type": file.content_type}
