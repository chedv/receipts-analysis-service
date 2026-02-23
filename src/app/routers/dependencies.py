from typing import AsyncGenerator
from urllib.parse import urljoin

import jwt
import redis.asyncio as redis
from aioboto3 import Session
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi_decorators import depends
from jwt import PyJWKClient, PyJWKClientError, DecodeError
from sqlalchemy.ext.asyncio import AsyncConnection
from starlette.requests import Request
from types_aiobotocore_s3 import S3Client

from src.app.exceptions import UnauthorizedException
from src.app.repositories.receipt_repository import ReceiptRepository
from src.app.database import Database
from src.app.services.receipt_service import ReceiptService
from src.settings import settings

http_bearer_token_auth = HTTPBearer()
jwks_client = PyJWKClient(uri=urljoin(settings.auth0_domain, "/.well-known/jwks.json"))


@depends
async def authenticate(auth_credentials: HTTPAuthorizationCredentials | None = Depends(http_bearer_token_auth)):
    if not auth_credentials:
        raise UnauthorizedException

    try:
        signing_key = jwks_client.get_signing_key_from_jwt(auth_credentials.credentials)
    except PyJWKClientError:
        raise UnauthorizedException

    try:
        return jwt.decode(
            auth_credentials.credentials,
            signing_key,
            algorithms=[settings.auth0_signing_algorithm],
            audience=settings.auth0_api_audience,
            issuer=settings.auth0_domain,
        )
    except DecodeError:
        raise UnauthorizedException


async def get_s3_client() -> AsyncGenerator[S3Client, None]:
    async with Session().client(
        service_name="s3",
        region_name=settings.aws_region,
        endpoint_url=settings.s3_endpoint,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
    ) as s3_client:
        yield s3_client


async def get_redis_client() -> redis.Redis:
    return redis.Redis(host=settings.redis_host, port=settings.redis_port)


async def get_database(request: Request) -> Database:
    return request.app.state.database


async def get_async_db_connection(
    database: Database = Depends(get_database)
) -> AsyncGenerator[AsyncConnection, None]:
    async with database.connect() as connection:
        yield connection


async def get_receipt_repository() -> ReceiptRepository:
    return ReceiptRepository()


async def get_receipt_service(
    s3_client: S3Client = Depends(get_s3_client),
    redis_client: redis.Redis = Depends(get_redis_client),
    database: Database = Depends(get_database),
    receipt_repository: ReceiptRepository = Depends(get_receipt_repository),
) -> ReceiptService:
    return ReceiptService(s3_client, redis_client, database, receipt_repository)
