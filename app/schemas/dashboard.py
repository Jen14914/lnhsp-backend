from pydantic import BaseModel


class AlertLevelSummary(BaseModel):
    level_number: int          # e.g. 2
    status_label: str          # "Elevated"


class KPISummary(BaseModel):
    alert_level: AlertLevelSummary
    active_outbreaks: int
    active_outbreaks_delta: int
    cases_this_week: int
    cases_pct_change: float
    deaths_this_week: int
    case_fatality_rate_pct: float
    districts_reporting: str       # "10/10"
    districts_reporting_pct: float


class DiseaseStatusPill(BaseModel):
    slug: str
    name: str
    status: str            # active/watch/routine/nocases
    cases_this_week: int
    trend_label: str       # "▲ 40% · Leribe"


class EpiCurvePoint(BaseModel):
    epi_week: int
    label: str              # "Wk13"
    total_cases: int
    threshold: int


class DistrictCasePoint(BaseModel):
    district: str
    case_count: int


class DiseaseShare(BaseModel):
    disease: str
    case_count: int


class TrendPoint(BaseModel):
    label: str
    case_count: int
    threshold: int | None = None


class DiseaseTrendSeries(BaseModel):
    disease_slug: str
    disease_name: str
    status: str
    points: list[TrendPoint]


class CompletenessCell(BaseModel):
    epi_week: int
    status: str


class CompletenessRow(BaseModel):
    district: str
    cells: list[CompletenessCell]


class SeasonalCell(BaseModel):
    month: int     # 1-12
    intensity: int  # 0-5


class SeasonalRow(BaseModel):
    disease: str
    cells: list[SeasonalCell]


class DashboardOverview(BaseModel):
    """One aggregate payload for the whole Dashboards tab (public view)."""
    kpi: KPISummary
    disease_pills: list[DiseaseStatusPill]
    epi_curve: list[EpiCurvePoint]
    cases_by_district: list[DistrictCasePoint]
    disease_share: list[DiseaseShare]
    trend_series: list[DiseaseTrendSeries]
    completeness: list[CompletenessRow]
    seasonal_calendar: list[SeasonalRow]
    last_synced: str
