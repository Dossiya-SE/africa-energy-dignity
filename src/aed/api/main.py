"""Africa Energy Dignity API application."""
from fastapi import FastAPI

from aed.api.routes import (
    assets,
    audit,
    geographies,
    health,
    institutions,
    projects,
    sources,
)

app = FastAPI(
    title="Africa Energy Dignity Registry API",
    version="0.1.0",
    description=(
        "Evidence, institution, geography, asset and project registry "
        "for the DATA-001 executable foundation."
    ),
)

for router in (
    health.router,
    sources.router,
    institutions.router,
    geographies.router,
    assets.router,
    projects.router,
    audit.router,
):
    app.include_router(router)
