"""Tests for async SQLModel repository."""

import pytest
import pytest_asyncio

sqlmodel = pytest.importorskip("sqlmodel")

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import SQLModel

from sqlrepository.async_repository import AsyncSQLModelRepository
from tests.sqlmodel_models import Album, Artist


# Test repositories
class ArtistRepository(AsyncSQLModelRepository[Artist, int]):
    """Repository for Artist model."""

    pass


class AlbumRepository(AsyncSQLModelRepository[Album, int]):
    """Repository for Album model."""

    pass


@pytest_asyncio.fixture
async def async_sqlmodel_session():
    """Create an async in-memory SQLite session for testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        # Add some test data
        artist1 = Artist(ArtistId=1, Name="AC/DC")
        artist2 = Artist(ArtistId=2, Name="Accept")
        session.add(artist1)
        session.add(artist2)
        await session.commit()

        album1 = Album(
            AlbumId=1,
            Title="For Those About To Rock We Salute You",
            ArtistId=1,
        )
        album2 = Album(AlbumId=2, Title="Let There Be Rock", ArtistId=1)
        session.add(album1)
        session.add(album2)
        await session.commit()

        yield session


@pytest.mark.asyncio
async def test_sqlmodel_repository_instantiation(
    async_sqlmodel_session: AsyncSession,
):
    """Test that AsyncSQLModelRepository can be instantiated."""
    repo = ArtistRepository(async_sqlmodel_session)
    assert repo is not None
    assert repo.session == async_sqlmodel_session
    assert repo.model == Artist


@pytest.mark.asyncio
async def test_sqlmodel_save(async_sqlmodel_session: AsyncSession):
    """Test saving a SQLModel entity."""
    repo = ArtistRepository(async_sqlmodel_session)
    artist = Artist(Name="Led Zeppelin")

    saved_artist = await repo.save(artist)
    await async_sqlmodel_session.commit()

    assert saved_artist.ArtistId is not None
    assert saved_artist.Name == "Led Zeppelin"


@pytest.mark.asyncio
async def test_sqlmodel_save_all(async_sqlmodel_session: AsyncSession):
    """Test saving multiple SQLModel entities."""
    repo = ArtistRepository(async_sqlmodel_session)
    artists = [
        Artist(Name="Led Zeppelin"),
        Artist(Name="Pink Floyd"),
    ]

    saved_artists = await repo.save_all(artists)
    await async_sqlmodel_session.commit()

    assert len(saved_artists) == 2
    assert all(a.ArtistId is not None for a in saved_artists)


@pytest.mark.asyncio
async def test_sqlmodel_find_by_id(async_sqlmodel_session: AsyncSession):
    """Test finding a SQLModel entity by ID."""
    repo = ArtistRepository(async_sqlmodel_session)

    found_artist = await repo.find_by_id(1)
    assert found_artist is not None
    assert found_artist.Name == "AC/DC"


@pytest.mark.asyncio
async def test_sqlmodel_find_all(async_sqlmodel_session: AsyncSession):
    """Test finding all SQLModel entities."""
    repo = ArtistRepository(async_sqlmodel_session)

    all_artists = await repo.find_all()
    assert len(all_artists) == 2
    assert {a.Name for a in all_artists} == {"AC/DC", "Accept"}


@pytest.mark.asyncio
async def test_sqlmodel_find_all_by_id(async_sqlmodel_session: AsyncSession):
    """Test finding multiple SQLModel entities by IDs."""
    repo = ArtistRepository(async_sqlmodel_session)
    ids = [1, 2]

    found_artists = await repo.find_all_by_id(ids)
    assert len(found_artists) == 2
    assert {a.Name for a in found_artists} == {"AC/DC", "Accept"}


@pytest.mark.asyncio
async def test_sqlmodel_count(async_sqlmodel_session: AsyncSession):
    """Test counting SQLModel entities."""
    repo = ArtistRepository(async_sqlmodel_session)

    count = await repo.count()
    assert count == 2


@pytest.mark.asyncio
async def test_sqlmodel_exists_by_id(async_sqlmodel_session: AsyncSession):
    """Test checking if a SQLModel entity exists."""
    repo = ArtistRepository(async_sqlmodel_session)

    exists = await repo.exists_by_id(1)
    assert exists is True

    not_exists = await repo.exists_by_id(999)
    assert not_exists is False


@pytest.mark.asyncio
async def test_sqlmodel_delete(async_sqlmodel_session: AsyncSession):
    """Test deleting a SQLModel entity."""
    repo = ArtistRepository(async_sqlmodel_session)
    artist = await repo.find_by_id(1)
    assert artist is not None

    await repo.delete(artist)
    await async_sqlmodel_session.commit()

    found_artist = await repo.find_by_id(1)
    assert found_artist is None


@pytest.mark.asyncio
async def test_sqlmodel_delete_by_id(async_sqlmodel_session: AsyncSession):
    """Test deleting a SQLModel entity by ID."""
    repo = ArtistRepository(async_sqlmodel_session)

    await repo.delete_by_id(1)
    await async_sqlmodel_session.commit()

    found_artist = await repo.find_by_id(1)
    assert found_artist is None


@pytest.mark.asyncio
async def test_sqlmodel_delete_all(async_sqlmodel_session: AsyncSession):
    """Test deleting all SQLModel entities."""
    repo = ArtistRepository(async_sqlmodel_session)

    await repo.delete_all()
    await async_sqlmodel_session.commit()

    count = await repo.count()
    assert count == 0


@pytest.mark.asyncio
async def test_sqlmodel_multiple_repositories(
    async_sqlmodel_session: AsyncSession,
):
    """Test using multiple async repositories with different SQLModel models."""
    artist_repo = ArtistRepository(async_sqlmodel_session)
    album_repo = AlbumRepository(async_sqlmodel_session)

    # Verify pre-loaded data
    assert await artist_repo.count() == 2
    assert await album_repo.count() == 2

    # Create new entities
    artist = Artist(Name="Iron Maiden")
    album = Album(Title="The Number of the Beast", ArtistId=1)

    await artist_repo.save(artist)
    await album_repo.save(album)
    await async_sqlmodel_session.commit()

    assert artist.ArtistId is not None
    assert album.AlbumId is not None

    found_artist = await artist_repo.find_by_id(artist.ArtistId)
    found_album = await album_repo.find_by_id(album.AlbumId)

    assert found_artist.Name == "Iron Maiden"
    assert found_album.Title == "The Number of the Beast"
    assert found_album.ArtistId == 1
