"""SQLAlchemy repository pattern implementation."""

from sqla_repository.core import Base, Repository
from sqla_repository.async_repository import AsyncRepository

try:
    from sqla_repository.core import SQLModelRepository
    from sqla_repository.async_repository import AsyncSQLModelRepository

    __all__ = [
        "Base",
        "Repository",
        "SQLModelRepository",
        "AsyncRepository",
        "AsyncSQLModelRepository",
    ]
except ImportError:
    # SQLModel not available
    __all__ = ["Base", "Repository", "AsyncRepository"]
