"""Async repository implementations for SQLAlchemy and SQLModel."""

from collections.abc import Iterable
from typing import Any, Generic, Sequence, TypeVar, cast, get_args, get_origin

from sqlalchemy import ColumnExpressionArgument, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

try:
    from sqlmodel import SQLModel

    SQLMODEL_AVAILABLE = True
except ImportError:
    SQLModel = None  # type: ignore
    SQLMODEL_AVAILABLE = False


# TypeVar definitions
EntityType = TypeVar("EntityType", bound=DeclarativeBase)
IdType = TypeVar("IdType")

if SQLMODEL_AVAILABLE:
    SQLModelEntityType = TypeVar("SQLModelEntityType", bound=SQLModel)  # type: ignore


class _AsyncRepositoryMixin(Generic[EntityType, IdType]):
    """
    Mixin containing all async repository CRUD operations.

    This mixin provides the async implementation that is shared between
    AsyncRepository (for SQLAlchemy) and AsyncSQLModelRepository (for SQLModel).
    """

    model: type[Any]
    session: AsyncSession

    def _model_type(self) -> type[EntityType]:
        """
        Returns the model type associated with this repository.

        Returns:
            type[EntityType]: The model class.
        """
        return cast(type[EntityType], self.__class__.model)

    async def save(self, entity: EntityType) -> EntityType:
        """
        Saves a given entity to the database.

        Args:
            entity (EntityType): The entity to save. Must not be None.

        Returns:
            EntityType: The saved entity.

        Raises:
            ValueError: If the entity is None.
        """
        if entity is None:
            raise ValueError("entity must not be None")
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def save_all(self, entities: Iterable[EntityType]) -> Sequence[EntityType]:
        """
        Saves all given entities to the database.

        Args:
            entities (Iterable[EntityType]): The entities to save. Must not contain None.

        Returns:
            Sequence[EntityType]: The saved entities.

        Raises:
            ValueError: If any entity is None.
        """
        items = list(entities)
        if any(entity is None for entity in items):
            raise ValueError("entities must not contain None")
        self.session.add_all(items)
        await self.session.flush()
        for entity in items:
            await self.session.refresh(entity)
        return items

    async def find_all(
        self,
        order_by: ColumnExpressionArgument[Any] | None = None,
    ) -> Sequence[EntityType]:
        """
        Returns all instances of the model type.

        Args:
            order_by: Optional column expression to order results by.

        Returns:
            Sequence[EntityType]: All entities in the database.
        """
        statement = select(self._model_type())

        if order_by is not None:
            statement = statement.order_by(order_by)

        result = await self.session.scalars(statement)
        return result.all()

    async def find_by_id(self, id: IdType) -> EntityType | None:
        """
        Retrieves an entity by its id.

        Args:
            id (IdType): The identifier of the entity. Must not be None.

        Returns:
            EntityType | None: The entity with the given id, or None if not found.

        Raises:
            ValueError: If id is None.
        """
        if id is None:
            raise ValueError("id must not be None")
        return await self.session.get(self._model_type(), id)

    async def exists_by_id(self, id: IdType) -> bool:
        """
        Returns whether an entity with the given id exists.

        Args:
            id (IdType): The identifier to check. Must not be None.

        Returns:
            bool: True if an entity with the given id exists, False otherwise.

        Raises:
            ValueError: If id is None.
        """
        if id is None:
            raise ValueError("id must not be None")
        return await self.find_by_id(id) is not None

    async def find_all_by_id(self, ids: Iterable[IdType]) -> Sequence[EntityType]:
        """
        Returns all entities matching the given ids.

        Args:
            ids (Iterable[IdType]): The identifiers of the entities. Must not contain None.

        Returns:
            Sequence[EntityType]: The found entities. Entities not found are omitted.

        Raises:
            ValueError: If any id is None.
        """
        id_values = list(ids)
        if any(id_value is None for id_value in id_values):
            raise ValueError("ids must not contain None")

        entities: list[EntityType] = []
        for id_value in id_values:
            entity = await self.find_by_id(id_value)
            if entity is not None:
                entities.append(entity)
        return entities

    async def count(self) -> int:
        """
        Returns the number of entities available.

        Returns:
            int: The count of entities in the database.
        """
        statement = select(func.count()).select_from(self._model_type())
        result = await self.session.scalar(statement)
        return int(result or 0)

    async def delete_by_id(self, id: IdType) -> None:
        """
        Deletes the entity with the given id.

        Args:
            id (IdType): The identifier of the entity to delete. Must not be None.

        Raises:
            ValueError: If id is None.
        """
        if id is None:
            raise ValueError("id must not be None")
        entity = await self.find_by_id(id)
        if entity is not None:
            await self.session.delete(entity)

    async def delete(self, entity: EntityType) -> None:
        """
        Deletes a given entity from the database.

        Args:
            entity (EntityType): The entity to delete. Must not be None.

        Raises:
            ValueError: If the entity is None.
        """
        if entity is None:
            raise ValueError("entity must not be None")
        await self.session.delete(entity)

    async def delete_all_by_id(self, ids: Iterable[IdType]) -> None:
        """
        Deletes all entities with the given ids.

        Args:
            ids (Iterable[IdType]): The identifiers of the entities to delete. Must not contain None.

        Raises:
            ValueError: If any id is None.
        """
        id_values = list(ids)
        if any(id_value is None for id_value in id_values):
            raise ValueError("ids must not contain None")
        for id_value in id_values:
            await self.delete_by_id(id_value)

    async def delete_all(self, entities: Iterable[EntityType] | None = None) -> None:
        """
        Deletes all entities in the database, or all given entities if provided.

        Args:
            entities (Iterable[EntityType] | None): The entities to delete. If None, deletes all entities of the model type.

        Raises:
            ValueError: If any entity in the provided iterable is None.
        """
        if entities is None:
            statement = delete(self._model_type())
            await self.session.execute(statement)
            return

        items = list(entities)
        if any(entity is None for entity in items):
            raise ValueError("entities must not contain None")
        for entity in items:
            await self.session.delete(entity)

    async def flush(self) -> None:
        """
        Flushes all pending changes to the database without committing them.
        """
        await self.session.flush()

    async def commit(self) -> None:
        """
        Commits the current transaction, making all pending changes permanent.
        """
        await self.session.commit()

    async def rollback(self) -> None:
        """
        Rolls back the current transaction, discarding all pending changes.
        """
        await self.session.rollback()


class AsyncRepository(_AsyncRepositoryMixin[EntityType, IdType]):
    """
    Generic async repository for SQLAlchemy DeclarativeBase models.

    This class is inspired by Spring Data's CrudRepository interface.
    Subclasses must specify the model type via AsyncRepository[Model, IdType].

    Example:
        ```python
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqla_repository import Base
        from sqla_repository.async_repository import AsyncRepository

        class User(Base):
            __tablename__ = "users"
            id: Mapped[int] = mapped_column(Integer, primary_key=True)
            name: Mapped[str] = mapped_column(String(50))

        class UserRepository(AsyncRepository[User, int]):
            pass

        # Usage
        async with AsyncSession(engine) as session:
            repo = UserRepository(session)
            user = await repo.find_by_id(1)
        ```
    """

    model: type[DeclarativeBase]

    def __init__(self, session: AsyncSession):
        """
        Initializes the repository with an async session.

        Args:
            session (AsyncSession): The async SQLAlchemy session to use.
        """
        self.session = session

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """
        Automatically sets the model type from the generic type argument.

        This is called when a subclass is created, allowing us to extract
        the model type from Repository[Model, IdType] syntax.
        """
        super().__init_subclass__(**kwargs)

        for base in cls.__orig_bases__:  # type: ignore
            origin = get_origin(base)
            if origin is None:
                continue

            if issubclass(origin, AsyncRepository):
                args = get_args(base)
                if args:
                    cls.model = args[0]
                    break


if SQLMODEL_AVAILABLE:

    class AsyncSQLModelRepository(_AsyncRepositoryMixin[SQLModelEntityType, IdType]):  # type: ignore
        """
        Generic async repository for SQLModel models.

        This class provides the same interface as AsyncRepository but is designed
        to work with SQLModel classes instead of SQLAlchemy DeclarativeBase.

        Example:
            ```python
            from sqlmodel import Field, SQLModel
            from sqlalchemy.ext.asyncio import AsyncSession
            from sqla_repository.async_repository import AsyncSQLModelRepository

            class User(SQLModel, table=True):
                id: int | None = Field(default=None, primary_key=True)
                name: str

            class UserRepository(AsyncSQLModelRepository[User, int]):
                pass

            # Usage
            async with AsyncSession(engine) as session:
                repo = UserRepository(session)
                user = await repo.find_by_id(1)
            ```
        """

        model: type[SQLModel]  # type: ignore

        def __init__(self, session: AsyncSession):
            """
            Initializes the repository with an async session.

            Args:
                session (AsyncSession): The async SQLAlchemy session to use.
            """
            self.session = session

        def __init_subclass__(cls, **kwargs: Any) -> None:
            """
            Automatically sets the model type from the generic type argument.

            This is called when a subclass is created, allowing us to extract
            the model type from AsyncSQLModelRepository[Model, IdType] syntax.
            """
            super().__init_subclass__(**kwargs)

            for base in cls.__orig_bases__:  # type: ignore
                origin = get_origin(base)
                if origin is None:
                    continue

                if issubclass(origin, AsyncSQLModelRepository):
                    args = get_args(base)
                    if args:
                        cls.model = args[0]
                        break


__all__ = ["AsyncRepository"]
if SQLMODEL_AVAILABLE:
    __all__.append("AsyncSQLModelRepository")
