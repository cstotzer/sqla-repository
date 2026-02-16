import datetime
import decimal
from typing import Optional

from sqlalchemy import (
    NVARCHAR,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    Table,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from sqla_repository.core import Base


class Artist(Base):
    __tablename__ = "artists"

    ArtistId: Mapped[int] = mapped_column(Integer, primary_key=True)
    Name: Mapped[Optional[str]] = mapped_column(NVARCHAR(120))

    albums: Mapped[list["Albums"]] = relationship(
        "Albums", back_populates="artist"
    )


class Employees(Base):
    __tablename__ = "employees"
    __table_args__ = (Index("IFK_EmployeeReportsTo", "ReportsTo"),)

    EmployeeId: Mapped[int] = mapped_column(
        "EmployeeId", Integer, primary_key=True
    )
    LastName: Mapped[str] = mapped_column(NVARCHAR(20), nullable=False)
    FirstName: Mapped[str] = mapped_column(NVARCHAR(20), nullable=False)
    Title: Mapped[Optional[str]] = mapped_column(NVARCHAR(30))
    ReportsTo: Mapped[Optional[int]] = mapped_column(
        ForeignKey("employees.EmployeeId")
    )
    BirthDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    HireDate: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    Address: Mapped[Optional[str]] = mapped_column(NVARCHAR(70))
    City: Mapped[Optional[str]] = mapped_column(NVARCHAR(40))
    State: Mapped[Optional[str]] = mapped_column(NVARCHAR(40))
    Country: Mapped[Optional[str]] = mapped_column(NVARCHAR(40))
    PostalCode: Mapped[Optional[str]] = mapped_column(NVARCHAR(10))
    Phone: Mapped[Optional[str]] = mapped_column(NVARCHAR(24))
    Fax: Mapped[Optional[str]] = mapped_column(NVARCHAR(24))
    Email: Mapped[Optional[str]] = mapped_column(NVARCHAR(60))

    employees: Mapped[Optional["Employees"]] = relationship(
        "Employees",
        remote_side=[EmployeeId],
        back_populates="employees_reverse",
    )
    employees_reverse: Mapped[list["Employees"]] = relationship(
        "Employees", remote_side=[ReportsTo], back_populates="employees"
    )
    customers: Mapped[list["Customers"]] = relationship(
        "Customers", back_populates="employees"
    )


class Genres(Base):
    __tablename__ = "genres"

    GenreId: Mapped[int] = mapped_column(Integer, primary_key=True)
    Name: Mapped[Optional[str]] = mapped_column(NVARCHAR(120))

    tracks: Mapped[list["Tracks"]] = relationship(
        "Tracks", back_populates="genres"
    )


class MediaTypes(Base):
    __tablename__ = "media_types"

    MediaTypeId: Mapped[int] = mapped_column(Integer, primary_key=True)
    Name: Mapped[Optional[str]] = mapped_column(NVARCHAR(120))

    tracks: Mapped[list["Tracks"]] = relationship(
        "Tracks", back_populates="media_types"
    )


class Playlists(Base):
    __tablename__ = "playlists"

    PlaylistId: Mapped[int] = mapped_column(Integer, primary_key=True)
    Name: Mapped[Optional[str]] = mapped_column(NVARCHAR(120))

    tracks: Mapped[list["Tracks"]] = relationship(
        "Tracks", secondary="playlist_track", back_populates="playlists"
    )


class Albums(Base):
    __tablename__ = "albums"
    __table_args__ = (Index("IFK_AlbumArtistId", "ArtistId"),)

    AlbumId: Mapped[int] = mapped_column(Integer, primary_key=True)
    Title: Mapped[str] = mapped_column(NVARCHAR(160), nullable=False)
    ArtistId: Mapped[int] = mapped_column(
        ForeignKey("artists.ArtistId"), nullable=False
    )

    artist: Mapped["Artist"] = relationship("Artist", back_populates="albums")
    tracks: Mapped[list["Tracks"]] = relationship(
        "Tracks", back_populates="albums"
    )


class Customers(Base):
    __tablename__ = "customers"
    __table_args__ = (Index("IFK_CustomerSupportRepId", "SupportRepId"),)

    CustomerId: Mapped[int] = mapped_column(Integer, primary_key=True)
    FirstName: Mapped[str] = mapped_column(NVARCHAR(40), nullable=False)
    LastName: Mapped[str] = mapped_column(NVARCHAR(20), nullable=False)
    Email: Mapped[str] = mapped_column(NVARCHAR(60), nullable=False)
    Company: Mapped[Optional[str]] = mapped_column(NVARCHAR(80))
    Address: Mapped[Optional[str]] = mapped_column(NVARCHAR(70))
    City: Mapped[Optional[str]] = mapped_column(NVARCHAR(40))
    State: Mapped[Optional[str]] = mapped_column(NVARCHAR(40))
    Country: Mapped[Optional[str]] = mapped_column(NVARCHAR(40))
    PostalCode: Mapped[Optional[str]] = mapped_column(NVARCHAR(10))
    Phone: Mapped[Optional[str]] = mapped_column(NVARCHAR(24))
    Fax: Mapped[Optional[str]] = mapped_column(NVARCHAR(24))
    SupportRepId: Mapped[Optional[int]] = mapped_column(
        ForeignKey("employees.EmployeeId")
    )

    employees: Mapped[Optional["Employees"]] = relationship(
        "Employees", back_populates="customers"
    )
    invoices: Mapped[list["Invoices"]] = relationship(
        "Invoices", back_populates="customers"
    )


class Invoices(Base):
    __tablename__ = "invoices"
    __table_args__ = (Index("IFK_InvoiceCustomerId", "CustomerId"),)

    InvoiceId: Mapped[int] = mapped_column(Integer, primary_key=True)
    CustomerId: Mapped[int] = mapped_column(
        ForeignKey("customers.CustomerId"), nullable=False
    )
    InvoiceDate: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False
    )
    Total: Mapped[decimal.Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    BillingAddress: Mapped[Optional[str]] = mapped_column(NVARCHAR(70))
    BillingCity: Mapped[Optional[str]] = mapped_column(NVARCHAR(40))
    BillingState: Mapped[Optional[str]] = mapped_column(NVARCHAR(40))
    BillingCountry: Mapped[Optional[str]] = mapped_column(NVARCHAR(40))
    BillingPostalCode: Mapped[Optional[str]] = mapped_column(NVARCHAR(10))

    customers: Mapped["Customers"] = relationship(
        "Customers", back_populates="invoices"
    )
    invoice_items: Mapped[list["InvoiceItems"]] = relationship(
        "InvoiceItems", back_populates="invoices"
    )


class Tracks(Base):
    __tablename__ = "tracks"
    __table_args__ = (
        Index("IFK_TrackAlbumId", "AlbumId"),
        Index("IFK_TrackGenreId", "GenreId"),
        Index("IFK_TrackMediaTypeId", "MediaTypeId"),
    )

    TrackId: Mapped[int] = mapped_column(Integer, primary_key=True)
    Name: Mapped[str] = mapped_column(NVARCHAR(200), nullable=False)
    MediaTypeId: Mapped[int] = mapped_column(
        ForeignKey("media_types.MediaTypeId"), nullable=False
    )
    Milliseconds: Mapped[int] = mapped_column(Integer, nullable=False)
    UnitPrice: Mapped[decimal.Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    AlbumId: Mapped[Optional[int]] = mapped_column(
        ForeignKey("albums.AlbumId")
    )
    GenreId: Mapped[Optional[int]] = mapped_column(
        ForeignKey("genres.GenreId")
    )
    Composer: Mapped[Optional[str]] = mapped_column(NVARCHAR(220))
    Bytes: Mapped[Optional[int]] = mapped_column(Integer)

    playlists: Mapped[list["Playlists"]] = relationship(
        "Playlists", secondary="playlist_track", back_populates="tracks"
    )
    albums: Mapped[Optional["Albums"]] = relationship(
        "Albums", back_populates="tracks"
    )
    genres: Mapped[Optional["Genres"]] = relationship(
        "Genres", back_populates="tracks"
    )
    media_types: Mapped["MediaTypes"] = relationship(
        "MediaTypes", back_populates="tracks"
    )
    invoice_items: Mapped[list["InvoiceItems"]] = relationship(
        "InvoiceItems", back_populates="tracks"
    )


class InvoiceItems(Base):
    __tablename__ = "invoice_items"
    __table_args__ = (
        Index("IFK_InvoiceLineInvoiceId", "InvoiceId"),
        Index("IFK_InvoiceLineTrackId", "TrackId"),
    )

    InvoiceLineId: Mapped[int] = mapped_column(Integer, primary_key=True)
    InvoiceId: Mapped[int] = mapped_column(
        ForeignKey("invoices.InvoiceId"), nullable=False
    )
    TrackId: Mapped[int] = mapped_column(
        ForeignKey("tracks.TrackId"), nullable=False
    )
    UnitPrice: Mapped[decimal.Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    Quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    invoices: Mapped["Invoices"] = relationship(
        "Invoices", back_populates="invoice_items"
    )
    tracks: Mapped["Tracks"] = relationship(
        "Tracks", back_populates="invoice_items"
    )


t_playlist_track = Table(
    "playlist_track",
    Base.metadata,
    Column("PlaylistId", ForeignKey("playlists.PlaylistId"), primary_key=True),
    Column("TrackId", ForeignKey("tracks.TrackId"), primary_key=True),
    Index("IFK_PlaylistTrackTrackId", "TrackId"),
)
