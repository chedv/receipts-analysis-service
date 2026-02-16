from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from src.app.database import Database
from src.app.urls import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.database = Database()
    await app.state.database.create_engine()
    yield
    await app.state.database.dispose_engine()


fastapi_app = FastAPI(lifespan=lifespan)

fastapi_app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)
