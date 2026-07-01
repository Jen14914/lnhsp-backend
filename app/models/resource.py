import enum
from datetime import date

from sqlalchemy import Column, Integer, String, Text, Date, Enum, Boolean

from app.database import Base


class ResourceCategory(str, enum.Enum):
    forms = "forms"
    sop = "sop"
    policy = "policy"
    training = "training"
    iec = "iec"


class Resource(Base):
    """A practical tool/template/SOP/policy document for field health workers."""

    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(200), unique=True, nullable=False, index=True)

    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(Enum(ResourceCategory), nullable=False)

    file_url = Column(String(500), nullable=False)
    file_format = Column(String(10), default="PDF")  # PDF, XLS, PPT, ZIP...
    version_label = Column(String(50), nullable=True)  # "Version 4.1" / "SOP-SURV-001 · v2.1"
    updated_date = Column(Date, nullable=False, default=date.today)

    is_quick_download = Column(Boolean, default=False)  # shown in the quick-download strip
    is_external_link = Column(Boolean, default=False)
