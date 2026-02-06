from fastapi import APIRouter, HTTPException, Depends
from schemas import ImageAnalysisRequest, HazardVerdict, HealthResponse
from service import get_vlm_service, VLMService

router = APIRouter()


@router.post("/analyze", response_model=HazardVerdict)
async def analyze_image(
    request: ImageAnalysisRequest,
    vlm: VLMService = Depends(get_vlm_service)
):
    """
    Analyze image for hazards using VLM
    
    - **image**: Base64 encoded image from phone camera
    - **label**: Suspected obstacle type from edge detector
    
    Returns detailed hazard assessment for TTS output
    """
    if not vlm.is_ready():
        raise HTTPException(status_code=503, detail="Model not loaded yet")
    
    verdict = vlm.analyze_hazard(request.image, request.label)
    return verdict


@router.get("/health", response_model=HealthResponse)
async def health_check(vlm: VLMService = Depends(get_vlm_service)):
    """
    Check if the VLM service is ready to accept requests
    """
    return HealthResponse(
        status="healthy" if vlm and vlm.is_ready() else "loading",
        model_loaded=vlm.is_ready() if vlm else False
    )