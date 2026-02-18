"""Tests for async Repository."""

import pytest
import pytest_asyncio
from sqlalchemy import Integer, String
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Mapped, mapped_column

from sqlrepository import Base
from sqlrepository.async_repository import AsyncRepository


# Test models
class AsyncArtist(Base):
    __tablename__ = "async_artists"

    ArtistId: Mapped[int] = mapped_column(Integer, primary_key=True)
    Name: Mapped[str | None] = mapped_column(String(120))


class AsyncAlbum(Base):
    __tablename__ = "async_albums"

    AlbumId: Mapped[int] = mapped_column(Integer, primary_key=True)
    Title: Mapped[str] = mapped_column(String(160), nullable=False)
    ArtistId: Mapped[int] = mapped_column(Integer, nullable=False)


# Test repositories
class ArtistRepository(AsyncRepository[AsyncArtist, int]):
    """Repository for Artist model."""

    pass


class AlbumRepository(AsyncRepository[AsyncAlbum, int]):
    """Repository for Album model."""

    pass


@pytest_asyncio.fixture
async def async_session():
    """Create an async in-memory SQLite session for testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        # Add some test data
        artist1 = AsyncArtist(ArtistId=1, Name="AC/DC")
        artist2 = AsyncArtist(ArtistId=2, Name="Accept")
        session.add(artist1)
        session.add(artist2)
        await session.commit()

        album1 = AsyncAlbum(
            AlbumId=1,
            Title="For Those About To Rock We Salute You",
            ArtistId=1,
        )
        album2 = AsyncAlbum(AlbumId=2, Title="Let There Be Rock", ArtistId=1)
        session.add(album1)
        session.add(album2)
        await session.commit()

        yield session


@pytest.mark.asyncio
async def test_repository_instantiation(async_session: AsyncSession):
    """Test that AsyncRepository can be instantiated."""
    repo = ArtistRepository(async_session)
    assert repo is not None
    assert repo.session == async_session
    assert repo.model == AsyncArtist


@pytest.mark.asyncio
async def test_save_entity(async_session: AsyncSession):
    """Test saving an entity."""
    repo = ArtistRepository(async_session)
    artist = AsyncArtist(Name="Led Zeppelin")

    saved_artist = await repo.save(artist)
    await async_session.commit()

    assert saved_artist.ArtistId is not None
    assert saved_artist.Name == "Led Zeppelin"


@pytest.mark.asyncio
async def test_save_all(async_session: AsyncSession):
    """Test saving multiple entities."""
    repo = ArtistRepository(async_session)
    artists = [
        AsyncArtist(Name="Led Zeppelin"),
        AsyncArtist(Name="Pink Floyd"),
    ]

    saved_artists = await repo.save_all(artists)
    await async_session.commit()

    assert len(saved_artists) == 2
    assert all(a.ArtistId is not None for a in saved_artists)


@pytest.mark.asyncio
async def test_find_by_id(async_session: AsyncSession):
    """Test finding an entity by ID."""
    repo = ArtistRepository(async_session)

    found_artist = await repo.find_by_id(1)
    assert found_artist is not None
    assert found_artist.Name == "AC/DC"


@pytest.mark.asyncio
async def test_find_by_id_not_found(async_session: AsyncSession):
    """Test finding a non-existent entity."""
    repo = ArtistRepository(async_session)

    found_artist = await repo.find_by_id(999)
    assert found_artist is None


@pytest.mark.asyncio
async def test_find_all(async_session: AsyncSession):
    """Test finding all entities."""
    repo = ArtistRepository(async_session)

    all_artists = await repo.find_all()
    assert len(all_artists) == 2
    assert {a.Name for a in all_artists} == {"AC/DC", "Accept"}


@pytest.mark.asyncio
async def test_find_all_by_id(async_session: AsyncSession):
    """Test finding entities by multiple IDs."""
    repo = ArtistRepository(async_session)
    ids = [1, 2]

    found_artists = await repo.find_all_by_id(ids)
    assert len(found_artists) == 2
    assert {a.Name for a in found_artists} == {"AC/DC", "Accept"}


@pytest.mark.asyncio
async def test_count(async_session: AsyncSession):
    """Test counting entities."""
    repo = ArtistRepository(async_session)

    count = await repo.count()
    assert count == 2


@pytest.mark.asyncio
async def test_exists_by_id(async_session: AsyncSession):
    """Test checking if an entity exists."""
    repo = ArtistRepository(async_session)

    exists = await repo.exists_by_id(1)
    assert exists is True

    not_exists = await repo.exists_by_id(999)
    assert not_exists is False


@pytest.mark.asyncio
async def test_delete_entity(async_session: AsyncSession):
    """Test deleting an entity."""
    repo = ArtistRepository(async_session)
    artist = await repo.find_by_id(1)
    assert artist is not None

    await repo.delete(artist)
    await async_session.commit()

    found_artist = await repo.find_by_id(1)
    assert found_artist is None


@pytest.mark.asyncio
async def test_delete_by_id(async_session: AsyncSession):
    """Test deleting an entity by ID."""
    repo = ArtistRepository(async_session)

    await repo.delete_by_id(1)
    await async_session.commit()

    found_artist = await repo.find_by_id(1)
    assert found_artist is None


@pytest.mark.asyncio
async def test_delete_all_by_id(async_session: AsyncSession):
    """Test deleting entities by IDs."""
    repo = ArtistRepository(async_session)
    ids = [1, 2]

    await repo.delete_all_by_id(ids)
    await async_session.commit()

    count = await repo.count()
    assert count == 0


@pytest.mark.asyncio
async def test_delete_all(async_session: AsyncSession):
    """Test deleting all entities."""
    repo = ArtistRepository(async_session)

    await repo.delete_all()
    await async_session.commit()

    count = await repo.count()
    assert count == 0


@pytest.mark.asyncio
async def test_delete_all_with_entities(async_session: AsyncSession):
    """Test deleting specific entities."""
    repo = ArtistRepository(async_session)
    artists = await repo.find_all()

    await repo.delete_all(artists)
    await async_session.commit()

    count = await repo.count()
    assert count == 0


@pytest.mark.asyncio
async def test_multiple_repositories(async_session: AsyncSession):
    """Test using multiple repositories with different models."""
    artist_repo = ArtistRepository(async_session)
    album_repo = AlbumRepository(async_session)

    # Verify pre-loaded data
    assert await artist_repo.count() == 2
    assert await album_repo.count() == 2

    # Create new entities
    artist = AsyncArtist(Name="Iron Maiden")
    album = AsyncAlbum(Title="The Number of the Beast", ArtistId=1)

    await artist_repo.save(artist)
    await album_repo.save(album)
    await async_session.commit()

    assert artist.ArtistId is not None
    assert album.AlbumId is not None

    found_artist = await artist_repo.find_by_id(artist.ArtistId)
    found_album = await album_repo.find_by_id(album.AlbumId)

    assert found_artist.Name == "Iron Maiden"
    assert found_album.Title == "The Number of the Beast"


@pytest.mark.asyncio
async def test_save_none_raises_error(async_session: AsyncSession):
    """Test that saving None raises ValueError."""
    repo = ArtistRepository(async_session)

    with pytest.raises(ValueError, match="entity must not be None"):
        await repo.save(None)  # type: ignore


@pytest.mark.asyncio
async def test_find_by_id_none_raises_error(async_session: AsyncSession):
    """Test that finding by None ID raises ValueError."""
    repo = ArtistRepository(async_session)

    with pytest.raises(ValueError, match="id must not be None"):
        await repo.find_by_id(None)  # type: ignore
