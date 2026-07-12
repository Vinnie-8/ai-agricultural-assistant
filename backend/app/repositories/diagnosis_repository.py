from uuid import UUID

from sqlalchemy.orm import Session

from app.models.diagnosis import Diagnosis


class DiagnosisRepository:
    @staticmethod
    def create(
        db: Session,
        **kwargs,
    ) -> Diagnosis:
        diagnosis = Diagnosis(**kwargs)
        db.add(diagnosis)
        db.commit()
        db.refresh(diagnosis)
        return diagnosis

    @staticmethod
    def get_by_id(db: Session, diagnosis_id: UUID) -> Diagnosis | None:
        return db.query(Diagnosis).filter(Diagnosis.id == diagnosis_id).first()