from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)

from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.repositories.diagnosis_repository import DiagnosisRepository
from app.schemas.diagnosis import DiagnosisResponse
from app.services.diagnosis_service import DiagnosisService

router = APIRouter(
    prefix="/diagnosis",
    tags=["Diagnosis"],
)


@router.post(
    "/predict",
    response_model=DiagnosisResponse,
    status_code=status.HTTP_201_CREATED,
)
async def predict_disease(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must be an image.",
        )

    image_path = await DiagnosisService.save_image(image)  # await stays — genuinely async
    prediction = DiagnosisService.predict(image_path)        # no await — now sync

    diagnosis = DiagnosisRepository.create(                   # no await — sync
        db=db,
        user_id=None,
        image_path=image_path,
        crop=prediction["crop"],
        disease=prediction["disease"],
        confidence=prediction["confidence"],
        recommendation=prediction["recommendation"],
        status=prediction["status"],
    )

    return diagnosis