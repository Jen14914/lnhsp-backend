import enum

from sqlalchemy import Column, Integer, String, Text, Enum, Float
from sqlalchemy.orm import relationship

from app.database import Base


class DiseaseStatus(str, enum.Enum):
    active = "active"      # active outbreak (red)
    watch = "watch"        # elevated / under watch (amber)
    routine = "routine"    # routine surveillance (green)
    nocases = "nocases"    # no cases currently reported


class DiseaseCategory(str, enum.Enum):
    idsr1 = "idsr1"
    idsr2 = "idsr2"
    vpd = "vpd"           # vaccine-preventable disease
    zoonotic = "zoonotic"
    sti = "sti"


class TrendDirection(str, enum.Enum):
    up = "up"
    down = "down"
    flat = "flat"


class Disease(Base):
    """A disease tracked under Lesotho's IDSR surveillance programme."""

    __tablename__ = "diseases"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(80), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False)
    sesotho_name = Column(String(150), nullable=True)
    letter = Column(String(1), nullable=False, index=True)  # for A-Z grouping

    category = Column(Enum(DiseaseCategory), nullable=False)
    status = Column(Enum(DiseaseStatus), nullable=False, default=DiseaseStatus.routine)
    idsr_priority = Column(String(50), nullable=False)  # "IDSR Priority 1" etc.
    transmission = Column(String(200), nullable=False)

    cases_this_week = Column(Integer, default=0)
    trend = Column(Enum(TrendDirection), default=TrendDirection.flat)
    trend_pct = Column(Float, nullable=True)  # e.g. 24.0 for "+24%"

    description = Column(Text, nullable=False)
    symptoms = Column(Text, nullable=False)   # newline-separated list
    prevention = Column(Text, nullable=False)
    when_to_seek_care = Column(Text, nullable=False)
    active_alert_note = Column(Text, nullable=True)  # shown as red box if set

    alerts = relationship("Alert", back_populates="disease")
    weekly_counts = relationship("DiseaseWeeklyCount", back_populates="disease")

    def symptoms_list(self) -> list[str]:
        return [s.strip() for s in self.symptoms.split("\n") if s.strip()]
