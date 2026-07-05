from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app import models  # noqa: F401 - ensures all models are registered before create_all
from app.routers import diseases, districts, alerts, publications, resources, reports, dashboards, auth, users

app = FastAPI(title=settings.app_name, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # Creates tables if they don't exist yet. For Postgres in production,
    # prefer running Alembic migrations instead (see backend/alembic/).
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"service": settings.app_name, "status": "ok"}


@app.get("/health")
def health():
    return {"status": "healthy"}


prefix = settings.api_v1_prefix
app.include_router(diseases.router, prefix=prefix)
app.include_router(districts.router, prefix=prefix)
app.include_router(alerts.router, prefix=prefix)
app.include_router(publications.router, prefix=prefix)
app.include_router(resources.router, prefix=prefix)
app.include_router(reports.router, prefix=prefix)
app.include_router(dashboards.router, prefix=prefix)
app.include_router(auth.router, prefix=prefix)
app.include_router(users.router, prefix=prefix)
