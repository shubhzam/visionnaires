"""API route modules."""

from __future__ import annotations

from .auth import router as auth_router
from .health import router as health_router
from .prediction import router as prediction_router
from .training import router as training_router
from .upload import router as upload_router
from .user import router as user_router

__all__ = [
	"auth_router",
	"health_router",
	"prediction_router",
	"training_router",
	"upload_router",
	"user_router",
]
