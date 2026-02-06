"""
FastAPI app optimized for mobile clients
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
import time

from src.api.routes import auth, upload, prediction, health, user
from src.logger.logging import Logger

logger = Logger(name="mobile_api")

app = FastAPI(
    title="Visionnaires Mobile API",
    description="Computer Vision API for Samsung S25 Ultra",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS - Allow your mobile app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specify your app's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compress responses (important for mobile)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"{request.method} {request.url.path} - {process_time:.3f}s")
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "detail": str(exc)
        }
    )

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(upload.router, prefix="/api/v1/upload", tags=["Upload"])
app.include_router(prediction.router, prefix="/api/v1/predict", tags=["Prediction"])
app.include_router(user.router, prefix="/api/v1/user", tags=["User"])

@app.on_event("startup")
async def startup_event():
    logger.info(" Mobile API starting up...")
    # Load ML model into memory here
    
@app.on_event("shutdown")
async def shutdown_event():
    logger.info(" Mobile API shutting down...")