import pytest

from tests.models import Albums, Artist
from tests.repositories import AlbumRepository, ArtistRepository


def test_count(artist_repository: ArtistRepository):
    cnt_artists = artist_repository.count()
    assert cnt_artists == 275


def test_find_all(artist_repository: ArtistRepository):
    artists = artist_repository.find_all()
    assert len(artists) == 275


def test_find_by_id(artist_repository: ArtistRepository):
    artist = artist_repository.find_by_id(252)
    assert artist is not None
    assert artist.ArtistId == 252
    assert artist.Name == "Amy Winehouse"


def test_find_all_by_id_error(artist_repository: ArtistRepository):
    try:
        artist_repository.find_all_by_id([1, 2, None])  # type: ignore[list-item]
        assert False, "Expected ValueError for None in IDs"
    except ValueError as e:
        assert str(e) == "ids must not contain None"


def test_find_by_id_not_found(artist_repository: ArtistRepository):
    artist = artist_repository.find_by_id(9999)
    assert artist is None


def test_find_all_by_id(artist_repository: ArtistRepository):
    artists = artist_repository.find_all_by_id([1, 2, 3, 9999])
    assert len(artists) == 3
    assert artists[0].ArtistId == 1
    assert artists[0].Name == "AC/DC"
    assert artists[1].ArtistId == 2
    assert artists[1].Name == "Accept"
    assert artists[2].ArtistId == 3
    assert artists[2].Name == "Aerosmith"


def test_save(artist_repository: ArtistRepository):
    cnt = artist_repository.count()
    new_artist = Artist(Name="Bad Omens")
    artist_repository.save(new_artist)
    artist_repository.session.commit()

    assert new_artist.ArtistId is not None

    found_artist = artist_repository.find_by_id(new_artist.ArtistId)
    assert found_artist is not None
    assert found_artist.Name == "Bad Omens"
    assert artist_repository.count() == cnt + 1


def test_save_all(artist_repository: ArtistRepository):
    cnt = artist_repository.count()
    new_artists = [Artist(Name="Bad Omens"), Artist(Name="Sleep Token")]
    artist_repository.save_all(new_artists)
    artist_repository.session.commit()

    assert new_artists[0].ArtistId is not None
    assert new_artists[1].ArtistId is not None

    found_artist_1 = artist_repository.find_by_id(new_artists[0].ArtistId)
    found_artist_2 = artist_repository.find_by_id(new_artists[1].ArtistId)
    assert found_artist_1 is not None
    assert found_artist_1.Name == "Bad Omens"
    assert found_artist_2 is not None
    assert found_artist_2.Name == "Sleep Token"
    assert artist_repository.count() == cnt + 2


def test_delete_by_id(artist_repository: ArtistRepository):
    new_artist = Artist(Name="Test Artist")
    artist_repository.save(new_artist)
    artist_repository.session.commit()

    assert new_artist.ArtistId is not None
    artist_id = new_artist.ArtistId

    artist_repository.delete_by_id(artist_id)
    artist_repository.session.commit()

    deleted_artist = artist_repository.find_by_id(artist_id)
    assert deleted_artist is None


def test_find_by_name(artist_repository: ArtistRepository):
    artists = artist_repository.find_by_name("AC/DC")
    assert len(artists) == 1
    assert artists[0].ArtistId == 1
    assert artists[0].Name == "AC/DC"


@pytest.mark.skip(reason="Ordering not implemented yet")
def test_find_all_ordered(artist_repository: ArtistRepository):
    artists = artist_repository.find_all(order_by=Artist.ArtistId)
    # assert len(artists) == 275
    assert artists[0].ArtistId == 43
    assert artists[1].ArtistId == 1
    assert artists[2].ArtistId == 230


def test_save_new_album(
    artist_repository: ArtistRepository,
    album_repository: AlbumRepository,
):

    nirvana: Artist = artist_repository.find_by_name("Nirvana")[0]
    new_album = Albums(Title="In Utero", artist=nirvana)
    album_repository.save(new_album)
    album_repository.session.commit()

    assert new_album.AlbumId is not None

    found_album = album_repository.find_by_id(new_album.AlbumId)
    assert found_album is not None
    assert found_album.Title == "In Utero"
    assert found_album.ArtistId == 110
