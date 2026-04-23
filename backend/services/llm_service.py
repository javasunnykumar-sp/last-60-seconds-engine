import os
import base64
import json
import re
import httpx
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, ValidationError


class AnalysisSchema(BaseModel):
    situation: str
    predicted_action: str
    risk: str
    recommended_action: str
    urgency: str
    urgency_reason: str
    confidence: float = Field(ge=0.0, le=1.0)
    why_this_matters: str


class LLMService:
    def __init__(self):
        self.base_url = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
        self.api_key = os.getenv("LM_STUDIO_API_KEY", "lm-studio")
        self.model_name = os.getenv("MODEL_NAME", "gemma-4")
        self.use_mock = os.getenv("USE_MOCK_ANALYZE", "False").lower() == "true"

    async def analyze_image(self, image_bytes: bytes, text_context: Optional[str] = None) -> Dict[str, Any]:
        if self.use_mock:
            return self._get_mock_response()

        base64_image = base64.b64encode(image_bytes).decode("utf-8")

        prompt = (
            "You are a real-world safety decision engine. "
            "Be practical, realistic, and non-alarmist. "
            "\nRules:" 
            "\n- Only mark HIGH if immediate serious harm is likely." 
            "\n- MEDIUM for moderate actionable risk." 
            "\n- LOW for minor or unlikely harm." 
            "\n- Recommendations must be specific and actionable." 
            "\n- Predicted action must describe likely human/agent behavior." 
            "\nReturn STRICT JSON:" 
            "{"
            "\"situation\": \"...\"," 
            "\"predicted_action\": \"what will likely happen next\"," 
            "\"risk\": \"realistic consequence\"," 
            "\"recommended_action\": \"specific immediate action\"," 
            "\"urgency\": \"low|medium|high\"," 
            "\"urgency_reason\": \"why this urgency was chosen\"," 
            "\"confidence\": 0.0," 
            "\"why_this_matters\": \"impact explanation\""
            "}" 
            f"\nContext: {text_context if text_context else 'None'}"
        )

        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                        },
                    ],
                }
            ],
            "temperature": 0.1,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=30.0,
                )
                response.raise_for_status()
            except Exception:
                return self._get_fallback_response("LLM unavailable")

        try:
            raw = response.json()["choices"][0]["message"]["content"]
            clean = re.sub(r"^```(?:json)?|```$", "", raw.strip(), flags=re.MULTILINE)
            data = json.loads(clean)
            return self._validate_schema(data)
        except Exception:
            return self._get_fallback_response("Invalid model output")

    def _validate_schema(self, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            validated = AnalysisSchema(**data)
            result = validated.model_dump()
            if result["urgency"] not in ["low", "medium", "high"]:
                result["urgency"] = "medium"
            return result
        except ValidationError:
            return self._get_fallback_response("Schema validation failed")

    def _get_fallback_response(self, reason: str) -> Dict[str, Any]:
        return {
            "situation": "Unable to analyze the situation",
            "predicted_action": "unknown",
            "risk": "unknown",
            "recommended_action": "Please review manually",
            "urgency": "low",
            "urgency_reason": "Fallback due to system limitations",
            "confidence": 0.5,
            "why_this_matters": reason,
        }

    def _get_mock_response(self) -> Dict[str, Any]:
        return {
            "situation": "Mock hazard",
            "predicted_action": "none",
            "risk": "low",
            "recommended_action": "observe",
            "urgency": "low",
            "urgency_reason": "mock mode",
            "confidence": 1.0,
            "why_this_matters": "test",
        }
