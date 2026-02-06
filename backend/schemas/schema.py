from pydantic import BaseModel, Field
from typing import Literal


class ImageAnalysisRequest(BaseModel):
    """Request payload from phone/client"""
    image: str = Field(..., description="Base64 encoded image string")
    label: str = Field(..., description="Suspected obstacle type from edge detector")


class HazardVerdict(BaseModel):
    """AI's analysis result"""
    hazard_detected: bool = Field(..., description="Whether a hazard is present")
    type: str = Field(..., description="Type of hazard (e.g. 'wet_floor', 'construction_barrier')")
    severity: Literal["low", "medium", "critical"] = Field(..., description="Danger level")
    action: str = Field(..., description="Recommended action (e.g. 'Stop', 'Go around')")
    description: str = Field(..., description="Concise description for TTS (max 10 words)")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool