from contextlib import asynccontextmanager, AbstractAsyncContextManager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncConnection, AsyncEngine

from src.settings import settings


class Database(AbstractAsyncContextManager):
    def __init__(self):
        self._engine: AsyncEngine | None = None

    async def create_engine(self):
        if self._engine is not None:
            raise RuntimeError("Database engine already initialized")

        self._engine = create_async_engine(settings.async_postgres_database_uri, pool_pre_ping=True)

    async def dispose_engine(self):
        if self._engine is None:
            raise RuntimeError("Database engine already disposed")

        await self._engine.dispose()

    async def __aenter__(self):
        await self.create_engine()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.dispose_engine()

    @asynccontextmanager
    async def connect(self) -> AsyncGenerator[AsyncConnection, None]:
        if self._engine is None:
            raise RuntimeError("Database engine is not initialized")

        async with self._engine.connect() as connection:
            yield connection

    @asynccontextmanager
    async def transactional(self) -> AsyncGenerator[AsyncConnection, None]:
        if self._engine is None:
            raise RuntimeError("Database engine is not initialized")

        async with self._engine.begin() as connection:
            yield connection
