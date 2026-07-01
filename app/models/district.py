from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class District(Base):
    """One of Lesotho's 10 administrative districts."""

    __tablename__ = "districts"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(50), unique=True, nullable=False, index=True)  # e.g. "leribe"
    name = Column(String(100), nullable=False)  # e.g. "Leribe"

    alerts = relationship("Alert", back_populates="district")
