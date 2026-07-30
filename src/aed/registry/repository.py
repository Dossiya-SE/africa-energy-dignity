"""Small repository layer with duplicate protection."""
from typing import TypeVar

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from aed.database.models import Base

ModelT = TypeVar("ModelT", bound=Base)


class DuplicateIdentifierError(ValueError):
    """Raised when a stable identifier or unique value already exists."""


def list_records(db: Session, model: type[ModelT]) -> list[ModelT]:
    """Return registry records in stable identifier order."""
    return list(db.scalars(select(model).order_by(model.id)).all())


def get_record(
    db: Session, model: type[ModelT], record_id: str
) -> ModelT | None:
    """Return one record by primary identifier."""
    return db.get(model, record_id)


def create_record(db: Session, model: type[ModelT], values: dict) -> ModelT:
    """Create without overwriting and translate integrity errors."""
    record = model(**values)
    db.add(record)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateIdentifierError(
            f"{model.__name__} identifier or unique value already exists."
        ) from exc
    return record
