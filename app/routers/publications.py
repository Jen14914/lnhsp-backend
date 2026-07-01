from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.publication import Publication, PublicationDiseaseTag
from app.schemas.publication import PublicationOut, PublicationCreate

router = APIRouter(prefix="/publications", tags=["publications"])

PAGE_SIZE = 9


@router.get("")
def list_publications(
    pub_type: str | None = Query(None),
    year: int | None = Query(None),
    disease: str | None = Query(None, description="disease slug"),
    search: str | None = Query(None),
    featured_only: bool = Query(False),
    page: int = Query(1, ge=1),
    db: Session = Depends(get_db),
):
    """
    Paginated publication archive with filters, matching the Publications tab's
    filter bar (type, year, disease, search) and featured strip.
    """
    q = db.query(Publication)
    if featured_only:
        q = q.filter(Publication.is_featured.is_(True))
    if pub_type and pub_type != "all":
        q = q.filter(Publication.pub_type == pub_type)
    if year and year != "all":
        q = q.filter(Publication.year == year)
    if disease:
        q = q.join(PublicationDiseaseTag).filter(
            PublicationDiseaseTag.disease_slug == disease
        )
    if search:
        q = q.filter(Publication.title.ilike(f"%{search}%"))

    total = q.count()
    items = (
        q.order_by(Publication.published_date.desc())
        .offset((page - 1) * PAGE_SIZE)
        .limit(PAGE_SIZE)
        .all()
    )
    return {
        "items": [PublicationOut.model_validate(p) for p in items],
        "total": total,
        "page": page,
        "page_size": PAGE_SIZE,
        "total_pages": (total + PAGE_SIZE - 1) // PAGE_SIZE if total else 1,
    }


@router.get("/{slug}", response_model=PublicationOut)
def get_publication(slug: str, db: Session = Depends(get_db)):
    pub = db.query(Publication).filter(Publication.slug == slug).first()
    if not pub:
        raise HTTPException(status_code=404, detail="Publication not found")
    return pub


@router.post("", response_model=PublicationOut, status_code=201)
def create_publication(payload: PublicationCreate, db: Session = Depends(get_db)):
    if db.query(Publication).filter(Publication.slug == payload.slug).first():
        raise HTTPException(status_code=409, detail="A publication with this slug already exists")
    pub = Publication(**payload.model_dump())
    db.add(pub)
    db.commit()
    db.refresh(pub)
    return pub
