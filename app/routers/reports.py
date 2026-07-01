from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.report import Report, DistrictCaseCount, DiseaseWeeklyCount
from app.schemas.report import (
    ReportListItem, ReportDetail, ReportCreate,
    DistrictCaseCountOut, DiseaseWeeklyCountOut,
)

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("", response_model=dict)
def list_reports(
    report_type: str = Query("weekly", description="weekly, district, sitrep, lab, dq"),
    year: int | None = Query(None),
    district: str | None = Query(None, description="district slug"),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
):
    """
    List reports filtered by type/year/district/search, plus counts per type
    (used by the report-type tab badges).
    """
    q = db.query(Report).options(joinedload(Report.district)).filter(
        Report.report_type == report_type
    )
    if year and year != "all":
        q = q.filter(Report.epi_year == year)
    if district and district != "all":
        q = q.join(Report.district).filter_by(slug=district)
    if search:
        q = q.filter(Report.title.ilike(f"%{search}%"))

    items = q.order_by(Report.published_date.desc()).all()

    from sqlalchemy import func
    type_counts_rows = (
        db.query(Report.report_type, func.count(Report.id)).group_by(Report.report_type).all()
    )
    type_counts = {
        (t.value if hasattr(t, "value") else t): n for t, n in type_counts_rows
    }

    return {
        "items": [ReportListItem.model_validate(r) for r in items],
        "type_counts": type_counts,
    }


@router.get("/active-sitreps", response_model=list[ReportListItem])
def active_sitreps(db: Session = Depends(get_db)):
    """Active situation reports shown in the red SitRep banner."""
    q = (
        db.query(Report)
        .options(joinedload(Report.district))
        .filter(Report.report_type == "sitrep", Report.is_sitrep_active.is_(True))
        .order_by(Report.published_date.desc())
    )
    return q.all()


@router.get("/{slug}", response_model=ReportDetail)
def get_report(slug: str, db: Session = Depends(get_db)):
    """Full report detail incl. preview-panel breakdowns, for the right-hand preview pane."""
    report = (
        db.query(Report)
        .options(
            joinedload(Report.district),
            joinedload(Report.district_breakdowns).joinedload(DistrictCaseCount.district),
            joinedload(Report.disease_breakdowns).joinedload(DiseaseWeeklyCount.disease),
        )
        .filter(Report.slug == slug)
        .first()
    )
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    district_breakdowns = [
        DistrictCaseCountOut(district=b.district, case_count=b.case_count)
        for b in report.district_breakdowns
    ]
    disease_breakdowns = [
        DiseaseWeeklyCountOut(
            disease_slug=b.disease.slug,
            disease_name=b.disease.name,
            case_count=b.case_count,
            trend=b.trend,
            trend_pct=b.trend_pct,
        )
        for b in report.disease_breakdowns
    ]

    # Build from scalar/relationship fields directly rather than letting
    # model_validate() walk report.disease_breakdowns / district_breakdowns
    # itself -- those ORM collections don't share attribute names with the
    # *_breakdowns output schemas (e.g. disease_slug/disease_name are
    # derived, not columns), so auto-validation against them fails.
    out = ReportDetail(
        id=report.id,
        slug=report.slug,
        report_type=report.report_type,
        title=report.title,
        published_date=report.published_date,
        epi_week=report.epi_week,
        epi_year=report.epi_year,
        file_size_mb=report.file_size_mb,
        sitrep_number=report.sitrep_number,
        is_sitrep_active=report.is_sitrep_active,
        district=report.district,
        file_url=report.file_url,
        active_outbreaks=report.active_outbreaks,
        total_cases=report.total_cases,
        deaths=report.deaths,
        districts_reporting=report.districts_reporting,
        district_breakdowns=district_breakdowns,
        disease_breakdowns=disease_breakdowns,
    )
    return out


@router.post("", response_model=ReportListItem, status_code=201)
def create_report(payload: ReportCreate, db: Session = Depends(get_db)):
    if db.query(Report).filter(Report.slug == payload.slug).first():
        raise HTTPException(status_code=409, detail="A report with this slug already exists")
    report = Report(**payload.model_dump())
    db.add(report)
    db.commit()
    db.refresh(report)
    return report
