from datetime import date
from pydantic import BaseModel, ConfigDict

from app.schemas.disease import DistrictOut


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    slug: str
    title: str
    body: str
    level: str
    tag: str
    published_date: date
    epi_week: int | None
    epi_year: int | None
    is_ticker: bool
    is_active: bool
    district: DistrictOut | None = None
    disease_slug: str | None = None


class AlertCreate(BaseModel):
    slug: str
    title: str
    body: str
    level: str
    tag: str
    published_date: date
    epi_week: int | None = None
    epi_year: int | None = None
    disease_id: int | None = None
    district_id: int | None = None
    is_ticker: bool = True
    is_active: bool = True
