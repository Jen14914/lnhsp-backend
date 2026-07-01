import enum
from datetime import date

from sqlalchemy import Column, Integer, String, Text, Date, Enum, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class PublicationType(str, enum.Enum):
    bulletin = "bulletin"
    outbreak = "outbreak"
    annual = "annual"
    guideline = "guideline"
    advisory = "advisory"
    research = "research"


class Publication(Base):
    """A formally released document (bulletin, outbreak report, guideline, etc.)."""

    __tablename__ = "publications"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(200), unique=True, nullable=False, index=True)

    title = Column(String(400), nullable=False)
    pub_type = Column(Enum(PublicationType), nullable=False)
    published_date = Column(Date, nullable=False, default=date.today)
    year = Column(Integer, nullable=False, index=True)

    file_url = Column(String(500), nullable=False)   # path/URL to the PDF
    file_format = Column(String(10), default="PDF")
    file_size_mb = Column(Float, nullable=True)

    is_featured = Column(Boolean, default=False)
    is_external_link = Column(Boolean, default=False)  # e.g. journal article (no download)

    disease_tags = relationship(
        "PublicationDiseaseTag", back_populates="publication", cascade="all, delete-orphan"
    )


class PublicationDiseaseTag(Base):
    """Many-to-many tag between publications and the diseases they cover."""

    __tablename__ = "publication_disease_tags"

    id = Column(Integer, primary_key=True, index=True)
    publication_id = Column(Integer, ForeignKey("publications.id"))
    disease_slug = Column(String(80), nullable=False)

    publication = relationship("Publication", back_populates="disease_tags")
