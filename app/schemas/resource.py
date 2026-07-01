from datetime import date
from pydantic import BaseModel, ConfigDict


class ResourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    slug: str
    title: str
    description: str
    category: str
    file_url: str
    file_format: str
    version_label: str | None
    updated_date: date
    is_quick_download: bool
    is_external_link: bool


class ResourceCreate(BaseModel):
    slug: str
    title: str
    description: str
    category: str
    file_url: str
    file_format: str = "PDF"
    version_label: str | None = None
    updated_date: date
    is_quick_download: bool = False
    is_external_link: bool = False
