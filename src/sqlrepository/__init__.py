"""SQLAlchemy repository pattern implementation."""

from sqlrepository.async_repository import AsyncRepository
from sqlrepository.core import Base, Repository

try:
    from sqlrepository.async_repository import AsyncSQLModelRepository
    from sqlrepository.core import SQLModelRepository

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
