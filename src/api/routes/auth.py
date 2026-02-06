"""Auth endpoints (JWT/login/etc.).

Stubs only — implement when you finalize auth strategy.
"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])
