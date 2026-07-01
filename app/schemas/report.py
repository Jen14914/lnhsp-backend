from datetime import date
from pydantic import BaseModel, ConfigDict

from app.schemas.disease import DistrictOut


class DistrictCaseCountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    district: DistrictOut
    case_count: int


class DiseaseWeeklyCountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    disease_slug: str
    disease_name: str
    case_count: int
    trend: str | None
    trend_pct: float | None


class ReportListItem(BaseModel):
    """Lightweight shape for report list rows."""
    model_config = ConfigDict(from_attributes=True)
    id: int
    slug: str
    report_type: str
    title: str
    published_date: date
    epi_week: int | None
    epi_year: int | None
    file_size_mb: float | None
    sitrep_number: int | None
    is_sitrep_active: bool
    district: DistrictOut | None = None


class ReportDetail(ReportListItem):
    """Full shape including the preview panel data."""
    file_url: str
    active_outbreaks: int | None
    total_cases: int | None
    deaths: int | None
    districts_reporting: str | None
    district_breakdowns: list[DistrictCaseCountOut] = []
    disease_breakdowns: list[DiseaseWeeklyCountOut] = []


class ReportCreate(BaseModel):
    slug: str
    report_type: str
    title: str
    published_date: date
    epi_week: int | None = None
    epi_year: int | None = None
    district_id: int | None = None
    disease_id: int | None = None
    file_url: str
    file_size_mb: float | None = None
    sitrep_number: int | None = None
    is_sitrep_active: bool = False
    active_outbreaks: int | None = None
    total_cases: int | None = None
    deaths: int | None = None
    districts_reporting: str | None = None
