from sqlrepository import Repository
from tests.models import Albums, Artist


class ArtistRepository(Repository[Artist, int]):
    def find_by_name(self, name: str) -> list[Artist]:
        """
        Finds artists by their name.

        Args:
            name (str): The name of the artist to search for.

        Returns:
            list[Artists]: A list of artists matching the given name.
        """
        return (
            self.session.query(self._model_type()).filter_by(Name=name).all()
        )


class AlbumRepository(Repository[Albums, int]): ...
