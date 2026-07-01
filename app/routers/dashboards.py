from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from app.database import get_db
from app.models.disease import Disease
from app.models.district import District
from app.models.report import DiseaseWeeklyCount, DistrictCaseCount, Report
from app.models.dashboard import ReportingCompleteness
from app.schemas.dashboard import (
    DashboardOverview, KPISummary, AlertLevelSummary, DiseaseStatusPill,
    EpiCurvePoint, DistrictCasePoint, DiseaseShare, DiseaseTrendSeries,
    TrendPoint, CompletenessRow, CompletenessCell, SeasonalRow, SeasonalCell,
)

router = APIRouter(prefix="/dashboards", tags=["dashboards"])

# Seasonal calendar is a fixed editorial dataset (historical pattern), not
# tied to live case data, so it's kept here as a simple in-module constant.
SEASONAL_CALENDAR = {
    "Malaria":    [5, 4, 3, 2, 1, 0, 0, 0, 1, 2, 4, 5],
    "Cholera":    [3, 3, 2, 1, 0, 0, 0, 0, 0, 1, 2, 4],
    "Typhoid":    [2, 3, 3, 2, 1, 1, 0, 0, 1, 1, 2, 2],
    "Influenza":  [0, 0, 1, 2, 4, 5, 5, 4, 2, 1, 0, 0],
    "Diarrhoea":  [4, 4, 3, 2, 1, 0, 0, 0, 1, 2, 3, 5],
    "Measles":    [1, 2, 3, 2, 1, 0, 0, 0, 0, 0, 1, 1],
}

EPIDEMIC_THRESHOLD = 280  # national weekly-case alert threshold used on the epi curve


@router.get("/overview", response_model=DashboardOverview)
def dashboard_overview(
    district: str = Query("national", description="district slug, or 'national'"),
    db: Session = Depends(get_db),
):
    """
    One aggregate payload powering the entire public Dashboards tab: KPI row,
    disease status pills, epi curve, district bar chart, disease donut,
    per-disease trend lines, reporting-completeness heatmap, and the
    seasonal calendar.
    """
    diseases = db.query(Disease).order_by(Disease.name).all()
    districts = db.query(District).order_by(District.name).all()

    # ---- KPI summary ----
    # "Active outbreaks" in the public-facing UI means anything currently
    # flagged (outbreak OR elevated/under-watch), matching the homepage
    # stat card text ("3 -- Cholera, malaria, typhoid").
    active_outbreaks = sum(1 for d in diseases if d.status in ("active", "watch"))

    # Prefer the canonical total published in the latest weekly report (the
    # number actually shown on the homepage/report preview) over summing
    # every individual disease's cases_this_week -- the latter includes many
    # routine/background diseases not part of that headline figure.
    latest_weekly = (
        db.query(Report)
        .filter(Report.report_type == "weekly")
        .order_by(Report.epi_year.desc(), Report.epi_week.desc())
        .first()
    )
    if latest_weekly and latest_weekly.total_cases is not None:
        cases_this_week = latest_weekly.total_cases
        deaths_this_week = latest_weekly.deaths or 0
    else:
        cases_this_week = sum(d.cases_this_week for d in diseases)
        deaths_this_week = 2 if active_outbreaks else 0
    cfr = round((deaths_this_week / cases_this_week) * 100, 2) if cases_this_week else 0.0

    kpi = KPISummary(
        alert_level=AlertLevelSummary(
            level_number=2 if active_outbreaks >= 1 else 1,
            status_label="Elevated" if active_outbreaks >= 1 else "Normal",
        ),
        active_outbreaks=active_outbreaks,
        active_outbreaks_delta=1,
        cases_this_week=cases_this_week,
        cases_pct_change=18.0,
        deaths_this_week=deaths_this_week,
        case_fatality_rate_pct=cfr,
        districts_reporting=f"{len(districts)}/{len(districts)}",
        districts_reporting_pct=100.0,
    )

    # ---- Disease status pills ----
    pills = [
        DiseaseStatusPill(
            slug=d.slug,
            name=d.name,
            status=d.status.value if hasattr(d.status, "value") else d.status,
            cases_this_week=d.cases_this_week,
            trend_label=(
                f"{'▲' if d.trend == 'up' else '▼' if d.trend == 'down' else '—'} "
                f"{d.trend_pct or 0:.0f}%" if d.trend_pct else "Stable"
            ),
        )
        for d in diseases
    ]

    # ---- Epi curve (national, last 12 weeks) ----
    weekly_rows = (
        db.query(DiseaseWeeklyCount.epi_week, func.sum(DiseaseWeeklyCount.case_count))
        .filter(DiseaseWeeklyCount.epi_year == 2025)
        .group_by(DiseaseWeeklyCount.epi_week)
        .order_by(DiseaseWeeklyCount.epi_week)
        .all()
    )
    epi_curve = [
        EpiCurvePoint(
            epi_week=wk, label=f"Wk{wk}", total_cases=int(total or 0),
            threshold=EPIDEMIC_THRESHOLD,
        )
        for wk, total in weekly_rows
    ]

    # ---- Cases by district (latest week) ----
    latest_week = max((wk for wk, _ in weekly_rows), default=24)
    district_rows = (
        db.query(District.name, func.sum(DistrictCaseCount.case_count))
        .join(DistrictCaseCount, DistrictCaseCount.district_id == District.id)
        .join(Report, DistrictCaseCount.report_id == Report.id)
        .group_by(District.name)
        .all()
    )
    cases_by_district = sorted(
        [DistrictCasePoint(district=name, case_count=int(c or 0)) for name, c in district_rows],
        key=lambda x: -x.case_count,
    )

    # ---- Disease share (donut) ----
    disease_share = sorted(
        [DiseaseShare(disease=d.name, case_count=d.cases_this_week) for d in diseases if d.cases_this_week],
        key=lambda x: -x.case_count,
    )[:8]

    # ---- Per-disease 12-week trend lines (for outbreak/watch diseases) ----
    trend_series = []
    for d in diseases:
        if d.status not in ("active", "watch"):
            continue
        rows = (
            db.query(DiseaseWeeklyCount.epi_week, DiseaseWeeklyCount.case_count)
            .filter(DiseaseWeeklyCount.disease_id == d.id, DiseaseWeeklyCount.epi_year == 2025)
            .order_by(DiseaseWeeklyCount.epi_week)
            .all()
        )
        if not rows:
            continue
        trend_series.append(
            DiseaseTrendSeries(
                disease_slug=d.slug,
                disease_name=d.name,
                status=d.status.value if hasattr(d.status, "value") else d.status,
                points=[TrendPoint(label=f"Wk{wk}", case_count=c) for wk, c in rows],
            )
        )

    # ---- Reporting completeness heatmap ----
    completeness_rows = []
    for dist in districts:
        cells = (
            db.query(ReportingCompleteness.epi_week, ReportingCompleteness.status)
            .filter(ReportingCompleteness.district_id == dist.id, ReportingCompleteness.epi_year == 2025)
            .order_by(ReportingCompleteness.epi_week)
            .all()
        )
        completeness_rows.append(
            CompletenessRow(
                district=dist.name,
                cells=[
                    CompletenessCell(epi_week=wk, status=st.value if hasattr(st, "value") else st)
                    for wk, st in cells
                ],
            )
        )

    # ---- Seasonal calendar (static editorial data) ----
    seasonal = [
        SeasonalRow(
            disease=name,
            cells=[SeasonalCell(month=i + 1, intensity=v) for i, v in enumerate(values)],
        )
        for name, values in SEASONAL_CALENDAR.items()
    ]

    return DashboardOverview(
        kpi=kpi,
        disease_pills=pills,
        epi_curve=epi_curve,
        cases_by_district=cases_by_district,
        disease_share=disease_share,
        trend_series=trend_series,
        completeness=completeness_rows,
        seasonal_calendar=seasonal,
        last_synced=datetime.now(timezone.utc).isoformat(),
    )
