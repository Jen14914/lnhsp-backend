from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.disease import Disease
from app.schemas.disease import DiseaseOut, DiseaseSummary

router = APIRouter(prefix="/diseases", tags=["diseases"])


@router.get("", response_model=list[DiseaseOut])
def list_diseases(
    category: str | None = Query(None, description="idsr1, idsr2, vpd, zoonotic, sti"),
    status: str | None = Query(None, description="active, watch, routine, nocases"),
    search: str | None = Query(None, description="Search by name or Sesotho name"),
    db: Session = Depends(get_db),
):
    """List all diseases for the Disease A-Z page, with optional filters."""
    q = db.query(Disease)
    if category and category != "all":
        q = q.filter(Disease.category == category)
    if status and status != "all":
        q = q.filter(Disease.status == status)
    if search:
        like = f"%{search.lower()}%"
        q = q.filter(
            (Disease.name.ilike(like))
            | (Disease.sesotho_name.ilike(like))
            | (Disease.description.ilike(like))
        )
    diseases = q.order_by(Disease.letter, Disease.name).all()
    return [DiseaseOut.from_orm_with_symptoms(d) for d in diseases]


@router.get("/status-summary", response_model=list[DiseaseSummary])
def disease_status_summary(db: Session = Depends(get_db)):
    """Lightweight list for the homepage status-pill strip / ticker."""
    diseases = db.query(Disease).order_by(Disease.name).all()
    return diseases


@router.get("/{slug}", response_model=DiseaseOut)
def get_disease(slug: str, db: Session = Depends(get_db)):
    disease = db.query(Disease).filter(Disease.slug == slug).first()
    if not disease:
        raise HTTPException(status_code=404, detail="Disease not found")
    return DiseaseOut.from_orm_with_symptoms(disease)
