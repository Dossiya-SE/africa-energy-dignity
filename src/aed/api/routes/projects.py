"""Project registry endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from aed.database.models import Project
from aed.database.session import get_db
from aed.registry.models import ProjectCreate, ProjectRead
from aed.registry.repository import DuplicateIdentifierError, list_records
from aed.registry.service import create_with_audit

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectRead])
def list_projects(db: Session = Depends(get_db)):
    """List project registry records."""
    return list_records(db, Project)


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    """Create a project without converting a fixture into a real claim."""
    try:
        return create_with_audit(
            db,
            model=Project,
            entity_type="project",
            values=payload.model_dump(mode="json"),
        )
    except DuplicateIdentifierError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
