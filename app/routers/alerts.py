from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.alert import Alert
from app.schemas.alert import AlertOut, AlertCreate

router = APIRouter(prefix="/alerts", tags=["alerts"])


def _to_out(a: Alert) -> AlertOut:
    out = AlertOut.model_validate(a)
    out.disease_slug = a.disease.slug if a.disease else None
    return out


@router.get("", response_model=list[AlertOut])
def list_alerts(
    level: str | None = Query(None),
    active_only: bool = Query(True),
    ticker_only: bool = Query(False),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
):
    """List alerts, most recent first. Used by the homepage feed and ticker."""
    q = db.query(Alert).options(joinedload(Alert.district), joinedload(Alert.disease))
    if active_only:
        q = q.filter(Alert.is_active.is_(True))
    if ticker_only:
        q = q.filter(Alert.is_ticker.is_(True))
    if level:
        q = q.filter(Alert.level == level)
    alerts = q.order_by(Alert.published_date.desc()).limit(limit).all()
    return [_to_out(a) for a in alerts]


@router.get("/{slug}", response_model=AlertOut)
def get_alert(slug: str, db: Session = Depends(get_db)):
    alert = (
        db.query(Alert)
        .options(joinedload(Alert.district), joinedload(Alert.disease))
        .filter(Alert.slug == slug)
        .first()
    )
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return _to_out(alert)


@router.post("", response_model=AlertOut, status_code=201)
def create_alert(payload: AlertCreate, db: Session = Depends(get_db)):
    """Create a new alert (e.g. from a surveillance officer's submission)."""
    if db.query(Alert).filter(Alert.slug == payload.slug).first():
        raise HTTPException(status_code=409, detail="An alert with this slug already exists")
    alert = Alert(**payload.model_dump())
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return _to_out(alert)
