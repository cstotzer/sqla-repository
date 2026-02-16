import sqlite3

from pytest import fixture
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from tests.repositories import AlbumRepository, ArtistRepository


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
