from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from services.llm_service import LLMService

app = FastAPI(title="Last 60 Seconds Engine API")
llm_service = LLMService()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    text_context: Optional[str] = Form(None),
):
    if not file or not file.content_type:
        raise HTTPException(
            status_code=400,
            detail="No file uploaded or content type missing.",
        )

    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload an image.",
        )

    image_bytes = await file.read()
    return await llm_service.analyze_image(image_bytes, text_context)
