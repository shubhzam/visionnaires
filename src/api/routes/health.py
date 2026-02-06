"""Health check endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from src.api.schemas.response import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok")
