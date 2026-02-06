"""Media schemas."""

from __future__ import annotations

from pydantic import BaseModel


class UploadResponse(BaseModel):
    filename: str
    content_type: str | None = None
