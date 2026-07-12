import requests

from app.core.config import settings


class AIServiceError(Exception):
    """Raised when the AI service call fails or times out."""


class AIClient:
    @staticmethod
    def chat(
        message: str,
        session_id: str,
        diagnosis_context: str | None = None,
        location: str | None = None,
    ) -> str:
        url = f"{settings.AI_SERVICE_URL}/api/v1/chat"

        payload = {
            "message": message,
            "session_id": session_id,
            "diagnosis_context": diagnosis_context,
             "location": location,
        }

        try:
            response = requests.post(url, json=payload, timeout=90)
            response.raise_for_status()
        except requests.RequestException as e:
            raise AIServiceError(f"AI service call failed: {e}") from e

        data = response.json()
        return data["reply"]