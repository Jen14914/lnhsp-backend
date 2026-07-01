import enum
from datetime import date

from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, Enum, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class AlertLevel(str, enum.Enum):
    red = "red"
    amber = "amber"
    green = "green"
    blue = "blue"


class AlertTag(str, enum.Enum):
    outbreak = "Outbreak"
    watch = "Watch"
    investigation = "Investigation"
    resolved = "Resolved"
    advisory = "Advisory"


class Alert(Base):
    """An outbreak alert / advisory shown on the homepage feed and ticker."""

    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(150), unique=True, nullable=False, index=True)

    title = Column(String(300), nullable=False)
    body = Column(Text, nullable=False)
    level = Column(Enum(AlertLevel), nullable=False)
    tag = Column(Enum(AlertTag), nullable=False)

    published_date = Column(Date, nullable=False, default=date.today)
    epi_week = Column(Integer, nullable=True)
    epi_year = Column(Integer, nullable=True)

    disease_id = Column(Integer, ForeignKey("diseases.id"), nullable=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=True)

    is_ticker = Column(Boolean, default=True)   # show in the scrolling ticker
    is_active = Column(Boolean, default=True)

    disease = relationship("Disease", back_populates="alerts")
    district = relationship("District", back_populates="alerts")
