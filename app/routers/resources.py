from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.resource import Resource
from app.schemas.resource import ResourceOut, ResourceCreate

router = APIRouter(prefix="/resources", tags=["resources"])


@router.get("", response_model=list[ResourceOut])
def list_resources(
    category: str | None = Query(None, description="forms, sop, policy, training, iec"),
    search: str | None = Query(None),
    quick_downloads_only: bool = Query(False),
    db: Session = Depends(get_db),
):
    q = db.query(Resource)
    if quick_downloads_only:
        q = q.filter(Resource.is_quick_download.is_(True))
    if category and category != "all":
        q = q.filter(Resource.category == category)
    if search:
        like = f"%{search}%"
        q = q.filter(
            (Resource.title.ilike(like)) | (Resource.description.ilike(like))
        )
    return q.order_by(Resource.category, Resource.title).all()


@router.get("/category-counts")
def category_counts(db: Session = Depends(get_db)):
    """Counts per category, used to populate the category filter tab badges."""
    from sqlalchemy import func

    rows = (
        db.query(Resource.category, func.count(Resource.id))
        .group_by(Resource.category)
        .all()
    )
    counts = {cat.value if hasattr(cat, "value") else cat: n for cat, n in rows}
    counts["all"] = sum(counts.values())
    return counts


@router.get("/{slug}", response_model=ResourceOut)
def get_resource(slug: str, db: Session = Depends(get_db)):
    resource = db.query(Resource).filter(Resource.slug == slug).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource


@router.post("", response_model=ResourceOut, status_code=201)
def create_resource(payload: ResourceCreate, db: Session = Depends(get_db)):
    if db.query(Resource).filter(Resource.slug == payload.slug).first():
        raise HTTPException(status_code=409, detail="A resource with this slug already exists")
    resource = Resource(**payload.model_dump())
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource
