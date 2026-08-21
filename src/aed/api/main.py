"""Africa Energy Dignity registry and transparent finance API."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from aed.api.routes import (
    assets,
    audit,
    finance,
    geographies,
    health,
    institutions,
    map_assets,
    projects,
    sources,
)

app = FastAPI(
    title="Africa Energy Dignity Registry API",
    version="0.4.0",
    description=(
        "Canonical evidence, institutional, geographic, geospatial-asset, project "
        "and transparent project-finance services for Africa Energy Dignity."
    ),
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
for router in (
    health.router,
    sources.router,
    institutions.router,
    geographies.router,
    assets.router,
    projects.router,
    audit.router,
    map_assets.router,
    finance.router,
):
    app.include_router(router)
