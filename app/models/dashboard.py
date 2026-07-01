import enum

from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class CompletenessStatus(str, enum.Enum):
    submitted = "submitted"
    late = "late"
    missing = "missing"


class ReportingCompleteness(Base):
    """
    One cell of the district x week reporting-completeness heatmap shown on
    the Dashboards tab.
    """

    __tablename__ = "reporting_completeness"

    id = Column(Integer, primary_key=True, index=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=False)
    epi_year = Column(Integer, nullable=False)
    epi_week = Column(Integer, nullable=False)
    status = Column(Enum(CompletenessStatus), nullable=False)

    district = relationship("District")
