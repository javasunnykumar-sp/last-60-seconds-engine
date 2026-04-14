import os
import base64
import json
import re
import httpx
from typing import Dict, Any, Optional
from fastapi import HTTPException
from pydantic import BaseModel, Field, ValidationError

# R20, R27: Enhanced schema with explainability field
class AnalysisSchema(BaseModel):
    situation: str
    predicted_action: str
    risk: str
    recommended_action: str
    urgency: str  # Must be low, medium, or high
    confidence: float = Field(ge=0.0, le=1.0)
    why_this_matters: str # R27: Added explainability

class LLMService:
    def __init__(self):
        # R18: Environment variable configuration
        self.base_url = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
        self.api_key = os.getenv("LM_STUDIO_API_KEY", "lm-studio")
        self.model_name = os.getenv("MODEL_NAME", "gemma-4")
        # FIX: Defaulting to False ensures it's REAL unless you explicitly set it to True
        self.use_mock = os.getenv("USE_MOCK_ANALYZE", "False").lower() == "true"

    async def analyze_image(self, image_bytes: bytes, text_context: Optional[str] = None) -> Dict[str, Any]:
        if self.use_mock:
            return self._get_mock_response()

        # 1. Prepare Image
        base64_image = base64.b64encode(image_bytes).decode('utf-8')

        # R26: Updated prompt for grounded reasoning and non-alarmist behavior
        prompt = (
            "You are a safety intervention engine. "
            "Your job is NOT to exaggerate risk. "
            "Rules: "
            "- Only mark urgency as HIGH if there is clear risk of serious injury or danger. "
            "- Use MEDIUM for moderate risk. "
            "- Use LOW for minor or negligible risk. "
            "- Be realistic and grounded. Avoid alarmist language. "
            "- Focus on immediate actionable advice. "
            "Return STRICT JSON only: "
            "{ "
            "\"situation\": \"...\", "
            "\"predicted_action\": \"...\", "
            "\"risk\": \"...\", "
            "\"recommended_action\": \"...\", "
            "\"urgency\": \"low | medium | high\", "
            "\"confidence\": 0.0, "
            "\"why_this_matters\": \"short explanation of consequence\" "
            "} "
            f"Context: {text_context if text_context else 'None'}"
        )

        payload: Dict[str, Any] = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url", 
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        }
                    ]
                }
            ],
            "temperature": 0.1,
        }

        # 3. Execute Request (R18, R21)
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=30.0
                )
                response.raise_for_status()
            except httpx.RequestError:
                # R28: Safe fallback for connection failure
                return self._get_fallback_response("LM Studio unavailable")
            except httpx.HTTPStatusError as e:
                # R28: Safe fallback for API error
                return self._get_fallback_response(f"LM Studio API error: {e.response.status_code}")

            # 4. Parse Response (R20, R22)
            try:
                resp_json = response.json()
                raw_content = resp_json["choices"][0]["message"]["content"]
                
                clean_json = raw_content.strip()
                if clean_json.startswith("```"):
                    # Remove markdown code blocks
                    clean_json = re.sub(r'^```(?:json)?|```$', '', clean_json, flags=re.MULTILINE).strip()
                
                data = json.loads(clean_json)
                return self._validate_schema(data)
            except (json.JSONDecodeError, KeyError, IndexError, ValueError):
                # R28: Safe fallback for malformed JSON
                return self._get_fallback_response("Model output invalid or malformed")

    def _validate_schema(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Uses Pydantic to enforce strict schema and types (R20, R29)."""
        try:
            validated = AnalysisSchema(**data)
            result = validated.model_dump()
            # Ensure urgency is strictly one of the allowed values
            if result["urgency"] not in ["low", "medium", "high"]:
                result["urgency"] = "medium"
            return result
        except ValidationError as e:
            # R28: If validation fails, return fallback instead of crashing
            return self._get_fallback_response(f"Schema validation failed: {str(e)}")

    # R28: Implementation of Safe Fallback Handling
    def _get_fallback_response(self, reason: str) -> Dict[str, Any]:
        return {
            "situation": "Unable to analyze the situation",
            "predicted_action": "unknown",
            "risk": "unknown",
            "recommended_action": "Please review the situation manually",
            "urgency": "low",
            "confidence": 0.5,
            "why_this_matters": f"Fallback triggered: {reason}"
        }

    def _get_mock_response(self) -> Dict[str, Any]:
        return {
            "situation": "Mocked safety hazard detected.",
            "predicted_action": "None",
            "risk": "Low (Mock Mode)",
            "recommended_action": "Observe system behavior.",
            "urgency": "low",
            "confidence": 1.0,
            "why_this_matters": "This is a simulated response for testing."
        }
    
        def _get_fallback_response(self):
            return AnalysisSchema(
            situation="System unavailable: Fallback mode active.",
            predicted_action="None (Service Offline)",
            risk="Unknown",
            recommended_action="Please check your local LM Studio connection.",
            urgency="low",
            confidence=0.0,
            why_this_matters="The AI engine is currently unreachable. Check connectivity."
        )