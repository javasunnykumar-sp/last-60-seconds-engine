from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Union
from services.llm_service import LLMService

app = FastAPI(title="Last 60 Seconds Engine API")
llm_service = LLMService()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    text_context: str = Form(None)
):
    # R14: Improved safety check for file and content_type
    if not file or not file.content_type:
        raise HTTPException(status_code=400, detail="No file uploaded or content type missing.")

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

    image_bytes = await file.read()
    
    # R18: Real inference via service
    result = await llm_service.analyze_image(image_bytes, text_context)
    return result

# 1. Define the Schema (Solves Type/Schema issues)
class AnalysisResponse(BaseModel):
    situation: str
    predicted_action: str
    risk: str
    recommended_action: str
    urgency: str
    confidence: float

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data - strictly typed to match AnalysisResponse
MOCK_RESULT: dict[str, Union[str, float]] = {
    "situation": "Loose exposed electrical wire near a plug point",
    "predicted_action": "ignore the wire and walk away",
    "risk": "short circuit, electric shock, or fire",
    "recommended_action": "turn off the power supply immediately and isolate the area",
    "urgency": "high",
    "confidence": 0.87
}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_situation(
    image: UploadFile = File(...),
    text_context: Optional[str] = Form(None) 
):
    # 2. Robust Content-Type Check (Solves potential NoneType errors)
    if image.content_type is None or not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Please upload an image."
        )

    # 3. Return the mock data (FastAPI will validate this against AnalysisResponse)
    return MOCK_RESULT