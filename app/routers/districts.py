from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.district import District
from app.schemas.disease import DistrictOut

router = APIRouter(prefix="/districts", tags=["districts"])


@router.get("", response_model=list[DistrictOut])
def list_districts(db: Session = Depends(get_db)):
    return db.query(District).order_by(District.name).all()
