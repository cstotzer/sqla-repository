"""SQLModel test models."""

from sqlmodel import Field, SQLModel


class Artist(SQLModel, table=True):
    """SQLModel artist model."""

    __tablename__ = "sqlmodel_artists"

    ArtistId: int | None = Field(default=None, primary_key=True)
    Name: str | None = Field(default=None, max_length=120)


class Album(SQLModel, table=True):
    """SQLModel album model."""

    __tablename__ = "sqlmodel_albums"

    AlbumId: int | None = Field(default=None, primary_key=True)
    Title: str = Field(max_length=160)
    ArtistId: int
