import sqlite3

from pytest import fixture
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from tests.repositories import AlbumRepository, ArtistRepository

try:
    from sqlmodel import SQLModel
    from sqlmodel import create_engine as sqlmodel_create_engine

    SQLMODEL_AVAILABLE = True
except ImportError:
    SQLMODEL_AVAILABLE = False


@fixture(scope="session", autouse=True)
def session():
    engine = create_engine("sqlite://", echo=True)
    connection = engine.raw_connection().driver_connection
    src = sqlite3.connect("tests/resources/chinook.db")
    if src and connection is not None:
        src.backup(connection)

    with Session(engine) as session:
        yield session

    session.close()


@fixture(scope="session", autouse=True)
def artist_repository(session):
    return ArtistRepository(session)


@fixture(scope="session", autouse=True)
def album_repository(session):
    return AlbumRepository(session)


@fixture(scope="function")
def sqlmodel_session():
    """Fixture for SQLModel tests with in-memory database."""
    if not SQLMODEL_AVAILABLE:
        import pytest

        pytest.skip("SQLModel not installed")

    engine = sqlmodel_create_engine("sqlite://", echo=True)
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    session.close()
