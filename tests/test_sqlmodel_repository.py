"""Tests for SQLModel compatibility with Repository."""

from sqlmodel import Field, SQLModel

from sqla_repository import SQLModelRepository


# SQLModel test models
class Hero(SQLModel, table=True):
    """SQLModel test model for heroes."""

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: int | None = None


class Team(SQLModel, table=True):
    """SQLModel test model for teams."""

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    headquarters: str


# Repository implementations
class HeroRepository(SQLModelRepository[Hero, int]):
    """Repository for Hero model."""

    pass


class TeamRepository(SQLModelRepository[Team, int]):
    """Repository for Team model."""

    pass


def test_sqlmodel_repository_instantiation(sqlmodel_session):
    """Test that repository can be instantiated with SQLModel."""
    repo = HeroRepository(sqlmodel_session)
    assert repo.model == Hero


def test_sqlmodel_save(sqlmodel_session):
    """Test saving a SQLModel entity."""
    repo = HeroRepository(sqlmodel_session)
    hero = Hero(name="Spider-Man", secret_name="Peter Parker", age=23)

    saved_hero = repo.save(hero)
    sqlmodel_session.commit()

    assert saved_hero.id is not None
    assert saved_hero.name == "Spider-Man"


def test_sqlmodel_find_by_id(sqlmodel_session):
    """Test finding a SQLModel entity by ID."""
    repo = HeroRepository(sqlmodel_session)
    hero = Hero(name="Iron Man", secret_name="Tony Stark", age=48)
    repo.save(hero)
    sqlmodel_session.commit()

    found_hero = repo.find_by_id(hero.id)
    assert found_hero is not None
    assert found_hero.name == "Iron Man"
    assert found_hero.secret_name == "Tony Stark"


def test_sqlmodel_find_all(sqlmodel_session):
    """Test finding all SQLModel entities."""
    repo = HeroRepository(sqlmodel_session)
    heroes = [
        Hero(name="Black Widow", secret_name="Natasha Romanoff", age=34),
        Hero(name="Captain America", secret_name="Steve Rogers", age=105),
        Hero(name="Hulk", secret_name="Bruce Banner", age=49),
    ]
    repo.save_all(heroes)
    sqlmodel_session.commit()

    all_heroes = repo.find_all()
    assert len(all_heroes) == 3
    assert all([h.id is not None for h in all_heroes])


def test_sqlmodel_count(sqlmodel_session):
    """Test counting SQLModel entities."""
    repo = HeroRepository(sqlmodel_session)
    heroes = [
        Hero(name="Thor", secret_name="Thor Odinson", age=1500),
        Hero(name="Hawkeye", secret_name="Clint Barton", age=40),
    ]
    repo.save_all(heroes)
    sqlmodel_session.commit()

    count = repo.count()
    assert count == 2


def test_sqlmodel_delete(sqlmodel_session):
    """Test deleting a SQLModel entity."""
    repo = HeroRepository(sqlmodel_session)
    hero = Hero(name="Loki", secret_name="Loki Laufeyson", age=1054)
    repo.save(hero)
    sqlmodel_session.commit()

    hero_id = hero.id
    repo.delete(hero)
    sqlmodel_session.commit()

    found_hero = repo.find_by_id(hero_id)
    assert found_hero is None


def test_sqlmodel_delete_by_id(sqlmodel_session):
    """Test deleting a SQLModel entity by ID."""
    repo = HeroRepository(sqlmodel_session)
    hero = Hero(name="Vision", secret_name="Vision", age=3)
    repo.save(hero)
    sqlmodel_session.commit()

    hero_id = hero.id
    repo.delete_by_id(hero_id)
    sqlmodel_session.commit()

    found_hero = repo.find_by_id(hero_id)
    assert found_hero is None


def test_sqlmodel_exists_by_id(sqlmodel_session):
    """Test checking if a SQLModel entity exists by ID."""
    repo = HeroRepository(sqlmodel_session)
    hero = Hero(name="Scarlet Witch", secret_name="Wanda Maximoff", age=29)
    repo.save(hero)
    sqlmodel_session.commit()

    exists = repo.exists_by_id(hero.id)
    assert exists is True

    not_exists = repo.exists_by_id(9999)
    assert not_exists is False


def test_sqlmodel_find_all_by_id(sqlmodel_session):
    """Test finding multiple SQLModel entities by IDs."""
    repo = HeroRepository(sqlmodel_session)
    heroes = [
        Hero(name="Ant-Man", secret_name="Scott Lang", age=39),
        Hero(name="Wasp", secret_name="Hope van Dyne", age=35),
        Hero(name="Doctor Strange", secret_name="Stephen Strange", age=42),
    ]
    repo.save_all(heroes)
    sqlmodel_session.commit()

    ids = [h.id for h in heroes]
    found_heroes = repo.find_all_by_id(ids)

    assert len(found_heroes) == 3
    assert all([h.id in ids for h in found_heroes])


def test_sqlmodel_save_all(sqlmodel_session):
    """Test saving multiple SQLModel entities."""
    repo = HeroRepository(sqlmodel_session)
    heroes = [
        Hero(name="Black Panther", secret_name="T'Challa", age=35),
        Hero(name="Star-Lord", secret_name="Peter Quill", age=38),
    ]

    saved_heroes = repo.save_all(heroes)
    sqlmodel_session.commit()

    assert len(saved_heroes) == 2
    assert all([h.id is not None for h in saved_heroes])


def test_sqlmodel_delete_all(sqlmodel_session):
    """Test deleting all SQLModel entities."""
    repo = HeroRepository(sqlmodel_session)
    heroes = [
        Hero(name="Gamora", secret_name="Gamora", age=29),
        Hero(name="Drax", secret_name="Drax the Destroyer", age=49),
    ]
    repo.save_all(heroes)
    sqlmodel_session.commit()

    repo.delete_all()
    sqlmodel_session.commit()

    count = repo.count()
    assert count == 0


def test_sqlmodel_multiple_repositories(sqlmodel_session):
    """Test using multiple repositories with different SQLModel models."""
    hero_repo = HeroRepository(sqlmodel_session)
    team_repo = TeamRepository(sqlmodel_session)

    hero = Hero(name="Captain Marvel", secret_name="Carol Danvers", age=35)
    team = Team(name="Avengers", headquarters="New York")

    hero_repo.save(hero)
    team_repo.save(team)
    sqlmodel_session.commit()

    assert hero.id is not None
    assert team.id is not None

    found_hero = hero_repo.find_by_id(hero.id)
    found_team = team_repo.find_by_id(team.id)

    assert found_hero.name == "Captain Marvel"
    assert found_team.name == "Avengers"
