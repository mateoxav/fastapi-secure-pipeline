from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Single declarative base for SQLAlchemy models."""
    pass

# Import models so that metadata is filled in for Alembic and testing
from app.models.user import User  # noqa: F401
from app.models.item import Item  # noqa: F401