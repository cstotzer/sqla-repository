# sqla-repository

A Python repository pattern implementation for SQLAlchemy and SQLModel, inspired by Spring Data's JPA Repositories.

## Overview

`sqla-repository` provides a clean, type-safe repository pattern for database operations, eliminating boilerplate CRUD code and promoting consistent data access patterns across your application. Whether you're using SQLAlchemy's `DeclarativeBase` or SQLModel's enhanced models with validation, this library offers a unified interface for your data access layer.

**Inspired by Spring Data JPA**, this package brings the elegant repository pattern from the Java ecosystem to Python, adapted for SQLAlchemy's powerful ORM capabilities.

### Key Features

- 🎯 **Type-safe** - Full type hints and generic support for IDE autocomplete
- 🔄 **Dual ORM support** - Works with both SQLAlchemy and SQLModel
- 🚀 **Zero boilerplate** - Common CRUD operations out of the box
- 🧩 **Extensible** - Easy to add custom query methods
- ✅ **Well-tested** - Comprehensive test suite with high coverage
- 📦 **Lightweight** - Minimal dependencies

## Installation

```bash
# Basic installation with SQLAlchemy support
pip install sqla-repository

# Or with Poetry
poetry add sqla-repository

# For SQLModel support (optional)
pip install sqla-repository[sqlmodel]
# or
poetry add sqla-repository --extras sqlmodel
```

## Usage

### Creating Repositories with SQLAlchemy

Define your model using SQLAlchemy's `DeclarativeBase`:

```python
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqla_repository import Base, Repository


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True)
    email: Mapped[str] = mapped_column(String(100))
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)


class UserRepository(Repository[User, int]):
    """Repository for User model."""
    pass
```

Use the repository in your application:

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

# Setup
engine = create_engine("sqlite:///app.db")
Base.metadata.create_all(engine)

with Session(engine) as session:
    user_repo = UserRepository(session)
    
    # Create
    new_user = User(username="john_doe", email="john@example.com", age=30)
    user_repo.save(new_user)
    session.commit()
    
    # Read
    user = user_repo.find_by_id(1)
    all_users = user_repo.find_all()
    
    # Update
    user.email = "newemail@example.com"
    user_repo.save(user)
    session.commit()
    
    # Delete
    user_repo.delete_by_id(1)
    session.commit()
    
    # Count
    total = user_repo.count()
```

### Creating Repositories with SQLModel

SQLModel combines SQLAlchemy's power with Pydantic's validation:

```python
from sqlmodel import Field, SQLModel
from sqla_repository import SQLModelRepository


class Artist(SQLModel, table=True):
    """SQLModel artist with built-in validation."""
    __tablename__ = "artists"
    
    ArtistId: int | None = Field(default=None, primary_key=True)
    Name: str = Field(index=True, min_length=1, max_length=120)


class ArtistRepository(SQLModelRepository[Artist, int]):
    """Repository for Artist model."""
    pass
```

Use with SQLModel:

```python
from sqlmodel import create_engine, Session, SQLModel

# Setup
engine = create_engine("sqlite:///music.db")
SQLModel.metadata.create_all(engine)

with Session(engine) as session:
    artist_repo = ArtistRepository(session)
    
    # Create with validation
    artist = Artist(Name="AC/DC")
    artist_repo.save(artist)
    session.commit()
    
    # Bulk operations
    artists = [
        Artist(Name="Led Zeppelin"),
        Artist(Name="Pink Floyd"),
    ]
    artist_repo.save_all(artists)
    session.commit()
```

### Adding Custom Query Methods

Extend the repository with your own query methods:

```python
from sqlalchemy import select
from sqla_repository import Repository


class UserRepository(Repository[User, int]):
    def find_by_username(self, username: str) -> User | None:
        """Find user by username."""
        statement = select(User).where(User.username == username)
        return self.session.scalar(statement)
    
    def find_by_age_range(self, min_age: int, max_age: int) -> list[User]:
        """Find users within age range."""
        statement = (
            select(User)
            .where(User.age >= min_age, User.age <= max_age)
            .order_by(User.age)
        )
        return list(self.session.scalars(statement))
    
    def find_active_users(self) -> list[User]:
        """Custom business logic query."""
        statement = (
            select(User)
            .where(User.is_active == True)
            .order_by(User.username)
        )
        return list(self.session.scalars(statement))
```

### Available Repository Methods

All repositories provide these methods out of the box:

**Create/Update:**
- `save(entity)` - Save or update a single entity
- `save_all(entities)` - Save or update multiple entities

**Read:**
- `find_by_id(id)` - Find entity by primary key
- `find_all()` - Get all entities
- `find_all_by_id(ids)` - Find multiple entities by IDs
- `exists_by_id(id)` - Check if entity exists
- `count()` - Count total entities

**Delete:**
- `delete(entity)` - Delete a single entity
- `delete_by_id(id)` - Delete by primary key
- `delete_all()` - Delete all entities
- `delete_all_by_id(ids)` - Delete multiple by IDs

**Transaction Control:**
- `flush()` - Flush pending changes
- `commit()` - Commit transaction
- `rollback()` - Rollback transaction

## Contributing

We welcome contributions! Here's how to get started:

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/cstotzer/sqla-repository.git
cd sqla-repository

# Install dependencies with Poetry
poetry install --with dev,sqlmodel

# Activate virtual environment
poetry shell
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=sqla_repository --cov-report=term-missing

# Run specific test file
poetry run pytest tests/test_repository.py -v

# Run specific test
poetry run pytest tests/test_repository.py::test_save -v
```

### Code Quality Checks

```bash
# Run linter
poetry run ruff check src tests

# Auto-fix linting issues
poetry run ruff check --fix src tests

# Format code
poetry run ruff format src tests

# Type checking
poetry run mypy src/sqla_repository --ignore-missing-imports
```

### Submitting Changes

1. **Fork the repository** on GitHub
2. **Create a feature branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** with clear, descriptive commits
4. **Ensure all tests pass** and code is properly formatted
5. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Open a Pull Request** on GitHub with:
   - Clear description of changes
   - Reference to any related issues
   - Test coverage for new features

### Pull Request Guidelines

- Follow existing code style and conventions
- Add tests for new functionality
- Update documentation if needed
- Keep changes focused and atomic
- Ensure CI checks pass before requesting review

### Release Process

Releases are managed through GitHub releases:

1. Version is bumped in `pyproject.toml`
2. Changes are committed and tagged (e.g., `v0.1.8`)
3. GitHub Actions builds and publishes to PyPI automatically
4. Release notes are generated from commit history

## License

This project is licensed under the **GNU General Public License v3.0**.

### What This Means

- ✅ **Free to use** - Use commercially or personally
- ✅ **Modify and distribute** - Make changes and share
- ⚠️ **Share alike** - Derivative works must use GPL-3.0
- ⚠️ **Disclose source** - Source code must be available
- ⚠️ **Include license** - Copy of GPL-3.0 must be included

See the [LICENSE](LICENSE) file for the full license text.

### Why GPL-3.0?

We believe in open source software and want to ensure that improvements to this library remain open and available to everyone. The GPL-3.0 license guarantees that all derivatives and modifications stay free and open source.

---

**Made with ❤️ by the sqla-repository contributors**
