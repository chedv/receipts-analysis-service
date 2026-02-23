from fastapi import HTTPException
from starlette import status


class UnauthorizedException(HTTPException):
    def __init__(self, detail=None):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)
