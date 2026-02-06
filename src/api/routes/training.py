"""Training endpoints (optional)."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/train", tags=["training"])


@router.post("/")
def train() -> dict:
    # Wire this to src/pipeline/training_pipeline.py later.
    return {"status": "not_implemented"}
