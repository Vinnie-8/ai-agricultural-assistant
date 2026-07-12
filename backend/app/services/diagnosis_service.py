from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageClassification

MODEL_NAME = "wambugu71/crop_leaf_diseases_vit"
CONFIDENCE_THRESHOLD = 0.65

_image_processor = AutoImageProcessor.from_pretrained(MODEL_NAME)
_model = AutoModelForImageClassification.from_pretrained(
    "wambugu1738/crop_leaf_diseases_vit",
    ignore_mismatched_sizes=True,
)
_model.eval()


def _parse_label(raw_label: str) -> tuple[str, str]:
    normalized = raw_label.replace("___", "_").replace(" - ", "_").replace("-", "_")
    parts = [p for p in normalized.split("_") if p]

    if len(parts) < 2:
        return "Unknown", raw_label

    crop = parts[0]
    disease = " ".join(parts[1:])
    return crop, disease


class DiagnosisService:

    UPLOAD_DIR = Path("uploads")

    @classmethod
    async def save_image(cls, image: UploadFile) -> str:
        cls.UPLOAD_DIR.mkdir(exist_ok=True)

        extension = image.filename.split(".")[-1]
        filename = f"{uuid4()}.{extension}"

        filepath = cls.UPLOAD_DIR / filename

        with open(filepath, "wb") as buffer:
            buffer.write(await image.read())

        return str(filepath)

    @classmethod
    def predict(cls, image_path: str) -> dict:
        image = Image.open(image_path).convert("RGB")

        inputs = _image_processor(images=image, return_tensors="pt")
        outputs = _model(**inputs)

        logits = outputs.logits
        probs = logits.softmax(dim=-1)

        predicted_idx = logits.argmax(-1).item()
        confidence = probs[0][predicted_idx].item()

        raw_label = _model.config.id2label[predicted_idx]
        print(f"[DiagnosisService] Raw model label: {raw_label!r}, confidence: {confidence:.4f}")

        if confidence < CONFIDENCE_THRESHOLD:
            return {
                "crop": "Unknown",
                "disease": "Unable to confidently identify",
                "confidence": round(confidence, 4),
                "recommendation": (
                    "This image doesn't clearly match a known crop leaf. "
                    "Please upload a clear, well-lit photo of a single leaf "
                    "for an accurate diagnosis."
                ),
                "status": "low_confidence",
            }

        crop, disease = _parse_label(raw_label)
        is_healthy = "healthy" in disease.lower()

        return {
            "crop": crop,
            "disease": disease,
            "confidence": round(confidence, 4),
            "recommendation": (
                "No treatment needed — plant appears healthy."
                if is_healthy
                else "Consult the chat assistant for tailored treatment advice."
            ),
            "status": "completed",
        }