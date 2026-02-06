"""Request schemas."""

from __future__ import annotations

from pydantic import BaseModel


class PredictionRequest(BaseModel):
    text: str
