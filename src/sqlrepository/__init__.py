"""SQLAlchemy repository pattern implementation."""

from sqlrepository.core import Base, Repository
from sqlrepository.async_repository import AsyncRepository

try:
    from sqlrepository.core import SQLModelRepository
    from sqlrepository.async_repository import AsyncSQLModelRepository

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
