import enum
from datetime import date

from sqlalchemy import (
    Column, Integer, String, Text, Date, Enum, Float, ForeignKey, Boolean
)
from sqlalchemy.orm import relationship

from app.database import Base


class ReportType(str, enum.Enum):
    weekly = "weekly"
    district = "district"
    sitrep = "sitrep"
    lab = "lab"
    dq = "dq"  # data quality


class Report(Base):
    """A report document: weekly epi report, district summary, sitrep, lab, or DQ report."""

    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(200), unique=True, nullable=False, index=True)

    report_type = Column(Enum(ReportType), nullable=False, index=True)
    title = Column(String(400), nullable=False)

    published_date = Column(Date, nullable=False, default=date.today)
    epi_week = Column(Integer, nullable=True)
    epi_year = Column(Integer, nullable=True, index=True)

    district_id = Column(Integer, ForeignKey("districts.id"), nullable=True)  # null = national
    disease_id = Column(Integer, ForeignKey("diseases.id"), nullable=True)    # for sitreps

    file_url = Column(String(500), nullable=False)
    file_size_mb = Column(Float, nullable=True)

    sitrep_number = Column(Integer, nullable=True)   # "SitRep #3"
    is_sitrep_active = Column(Boolean, default=False)

    # Preview summary fields (used by the report preview panel)
    active_outbreaks = Column(Integer, nullable=True)
    total_cases = Column(Integer, nullable=True)
    deaths = Column(Integer, nullable=True)
    districts_reporting = Column(String(20), nullable=True)  # e.g. "10/10"

    district = relationship("District")
    disease = relationship("Disease")
    district_breakdowns = relationship(
        "DistrictCaseCount", back_populates="report", cascade="all, delete-orphan"
    )
    disease_breakdowns = relationship(
        "DiseaseWeeklyCount", back_populates="report", cascade="all, delete-orphan"
    )


class DistrictCaseCount(Base):
    """Per-district case counts attached to a report's preview ('Cases by district')."""

    __tablename__ = "report_district_counts"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)
    case_count = Column(Integer, nullable=False, default=0)

    report = relationship("Report", back_populates="district_breakdowns")
    district = relationship("District")


class DiseaseWeeklyCount(Base):
    """
    Per-disease weekly case counts. Used both for:
      - a report's 'Top diseases this week' preview panel (report_id set)
      - the 12-week epi-curve / trend charts on the dashboard (report_id null, just disease+week)
    """

    __tablename__ = "disease_weekly_counts"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=True)
    disease_id = Column(Integer, ForeignKey("diseases.id"), nullable=False)

    epi_year = Column(Integer, nullable=False)
    epi_week = Column(Integer, nullable=False)
    case_count = Column(Integer, nullable=False, default=0)
    trend = Column(Enum("up", "down", "flat", name="weekly_trend"), nullable=True)
    trend_pct = Column(Float, nullable=True)

    report = relationship("Report", back_populates="disease_breakdowns")
    disease = relationship("Disease", back_populates="weekly_counts")
