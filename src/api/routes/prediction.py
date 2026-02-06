"""Prediction endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from src.api.schemas.request import PredictionRequest
from src.api.schemas.response import PredictionResponse

router = APIRouter(prefix="/predict", tags=["prediction"])


@router.post("/", response_model=PredictionResponse)
def predict(payload: PredictionRequest) -> PredictionResponse:
    # Wire this to your pipeline in src/pipeline/prediction_pipeline.py later.
    return PredictionResponse(result=payload.text)
