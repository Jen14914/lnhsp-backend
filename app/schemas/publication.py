from datetime import date
from pydantic import BaseModel, ConfigDict


class PublicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    slug: str
    title: str
    pub_type: str
    published_date: date
    year: int
    file_url: str
    file_format: str
    file_size_mb: float | None
    is_featured: bool
    is_external_link: bool


class PublicationCreate(BaseModel):
    slug: str
    title: str
    pub_type: str
    published_date: date
    year: int
    file_url: str
    file_format: str = "PDF"
    file_size_mb: float | None = None
    is_featured: bool = False
    is_external_link: bool = False
