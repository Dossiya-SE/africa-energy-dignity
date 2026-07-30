"""Health endpoint."""
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    """Return a dependency-free process health response."""
    return {"status": "ok", "service": "africa-energy-dignity-api"}
