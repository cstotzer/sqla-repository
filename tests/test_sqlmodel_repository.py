"""Tests for SQLModel compatibility with Repository."""

import pytest

sqlmodel = pytest.importorskip("sqlmodel")

from sqlmodel import Session, SQLModel, create_engine

from sqlrepository import SQLModelRepository
from tests.sqlmodel_models import Album, Artist


# Repository implementations
class ArtistRepository(SQLModelRepository[Artist, int]):
    """Repository for Artist model."""

    pass


class AlbumRepository(SQLModelRepository[Album, int]):
    """Repository for Album model."""

    pass


@pytest.fixture(scope="function")
def sqlmodel_session():
    """Create an in-memory SQLite database session for testing."""
    engine = create_engine(
        "sqlite:///:memory:", connect_args={"check_same_thread": False}
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        # Add some test data
        artist1 = Artist(ArtistId=1, Name="AC/DC")
        artist2 = Artist(ArtistId=2, Name="Accept")
        session.add(artist1)
        session.add(artist2)
        session.commit()

        album1 = Album(
            AlbumId=1,
            Title="For Those About To Rock We Salute You",
            ArtistId=1,
        )
        album2 = Album(AlbumId=2, Title="Let There Be Rock", ArtistId=1)
        session.add(album1)
        session.add(album2)
        session.commit()

        yield session


def test_sqlmodel_repository_instantiation(sqlmodel_session):
    """Test that repository can be instantiated with SQLModel."""
    repo = ArtistRepository(sqlmodel_session)
    assert repo.model == Artist


def test_sqlmodel_save(sqlmodel_session):
    """Test saving a SQLModel entity."""
    repo = ArtistRepository(sqlmodel_session)
    artist = Artist(Name="Led Zeppelin")

    saved_artist = repo.save(artist)
    sqlmodel_session.commit()

    assert saved_artist.ArtistId is not None
    assert saved_artist.Name == "Led Zeppelin"


def test_sqlmodel_find_by_id(sqlmodel_session):
    """Test finding a SQLModel entity by ID."""
    repo = ArtistRepository(sqlmodel_session)

    found_artist = repo.find_by_id(1)
    assert found_artist is not None
    assert found_artist.Name == "AC/DC"


def test_sqlmodel_find_all(sqlmodel_session):
    """Test finding all SQLModel entities."""
    repo = ArtistRepository(sqlmodel_session)

    all_artists = repo.find_all()
    assert len(all_artists) == 2  # AC/DC and Accept from fixture
    assert all([a.ArtistId is not None for a in all_artists])


def test_sqlmodel_count(sqlmodel_session):
    """Test counting SQLModel entities."""
    repo = ArtistRepository(sqlmodel_session)

    count = repo.count()
    assert count == 2  # AC/DC and Accept from fixture


def test_sqlmodel_delete(sqlmodel_session):
    """Test deleting a SQLModel entity."""
    repo = ArtistRepository(sqlmodel_session)
    artist = repo.find_by_id(1)
    assert artist is not None

    repo.delete(artist)
    sqlmodel_session.commit()

    found_artist = repo.find_by_id(1)
    assert found_artist is None


def test_sqlmodel_delete_by_id(sqlmodel_session):
    """Test deleting a SQLModel entity by ID."""
    repo = ArtistRepository(sqlmodel_session)

    repo.delete_by_id(1)
    sqlmodel_session.commit()

    found_artist = repo.find_by_id(1)
    assert found_artist is None


def test_sqlmodel_exists_by_id(sqlmodel_session):
    """Test checking if a SQLModel entity exists by ID."""
    repo = ArtistRepository(sqlmodel_session)

    exists = repo.exists_by_id(1)
    assert exists is True

    not_exists = repo.exists_by_id(9999)
    assert not_exists is False


def test_sqlmodel_find_all_by_id(sqlmodel_session):
    """Test finding multiple SQLModel entities by IDs."""
    repo = ArtistRepository(sqlmodel_session)
    ids = [1, 2]

    found_artists = repo.find_all_by_id(ids)

    assert len(found_artists) == 2
    assert {a.Name for a in found_artists} == {"AC/DC", "Accept"}


def test_sqlmodel_save_all(sqlmodel_session):
    """Test saving multiple SQLModel entities."""
    repo = ArtistRepository(sqlmodel_session)
    artists = [
        Artist(Name="Led Zeppelin"),
        Artist(Name="Pink Floyd"),
    ]

    saved_artists = repo.save_all(artists)
    sqlmodel_session.commit()

    assert len(saved_artists) == 2
    assert all([a.ArtistId is not None for a in saved_artists])


def test_sqlmodel_delete_all(sqlmodel_session):
    """Test deleting all SQLModel entities."""
    repo = ArtistRepository(sqlmodel_session)

    repo.delete_all()
    sqlmodel_session.commit()

    count = repo.count()
    assert count == 0


def test_sqlmodel_multiple_repositories(sqlmodel_session):
    """Test using multiple repositories with different SQLModel models."""
    artist_repo = ArtistRepository(sqlmodel_session)
    album_repo = AlbumRepository(sqlmodel_session)

    # Verify pre-loaded data
    assert artist_repo.count() == 2
    assert album_repo.count() == 2

    # Create new entities
    artist = Artist(Name="Iron Maiden")
    album = Album(Title="The Number of the Beast", ArtistId=1)

    artist_repo.save(artist)
    album_repo.save(album)
    sqlmodel_session.commit()

    assert artist.ArtistId is not None
    assert album.AlbumId is not None

    found_artist = artist_repo.find_by_id(artist.ArtistId)
    found_album = album_repo.find_by_id(album.AlbumId)

    assert found_artist.Name == "Iron Maiden"
    assert found_album.Title == "The Number of the Beast"
    assert found_album.ArtistId == 1  # Belongs to AC/DC
