"""SQLAlchemy repository pattern implementation."""

from sqla_repository.core import Base, Repository

try:
    from sqla_repository.core import SQLModelRepository

    __all__ = ["Base", "Repository", "SQLModelRepository"]
except ImportError:
    # SQLModel not available
    __all__ = ["Base", "Repository"]
