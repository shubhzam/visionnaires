"""API route modules."""

from __future__ import annotations

from .health import router as health_router
from .prediction import router as prediction_router
from .training import router as training_router
from .upload import router as upload_router

__all__ = [
	"health_router",
	"prediction_router",
	"training_router",
	"upload_router",
]
