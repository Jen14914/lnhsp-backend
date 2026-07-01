from datetime import date
from pydantic import BaseModel, ConfigDict


class DistrictOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    slug: str
    name: str


class DiseaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    slug: str
    name: str
    sesotho_name: str | None
    letter: str
    category: str
    status: str
    idsr_priority: str
    transmission: str
    cases_this_week: int
    trend: str
    trend_pct: float | None
    description: str
    prevention: str
    when_to_seek_care: str
    active_alert_note: str | None
    symptoms: list[str]

    @classmethod
    def from_orm_with_symptoms(cls, obj):
        data = {c: getattr(obj, c) for c in [
            "id", "slug", "name", "sesotho_name", "letter", "category", "status",
            "idsr_priority", "transmission", "cases_this_week", "trend", "trend_pct",
            "description", "prevention", "when_to_seek_care", "active_alert_note",
        ]}
        data["category"] = obj.category.value if hasattr(obj.category, "value") else obj.category
        data["status"] = obj.status.value if hasattr(obj.status, "value") else obj.status
        data["trend"] = obj.trend.value if hasattr(obj.trend, "value") else obj.trend
        data["symptoms"] = obj.symptoms_list()
        return cls(**data)


class DiseaseSummary(BaseModel):
    """Lightweight disease shape for the status-pill strip / ticker."""
    model_config = ConfigDict(from_attributes=True)
    slug: str
    name: str
    status: str
    cases_this_week: int
