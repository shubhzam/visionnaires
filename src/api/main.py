"""FastAPI application entry point."""

from __future__ import annotations

from fastapi import FastAPI

from src.api.routes import health_router, prediction_router, training_router, upload_router


def create_app() -> FastAPI:
	app = FastAPI(title="visionnaires")
	app.include_router(health_router)
	app.include_router(prediction_router)
	app.include_router(training_router)
	app.include_router(upload_router)
	return app


app = create_app()
