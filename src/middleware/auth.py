from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from config import settings

UNPROTECTED = {"/docs", "/openapi.json", "/redoc", "/api/openapi.json"}


class ApiKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in UNPROTECTED:
            return await call_next(request)

        key = request.headers.get("X-API-Key", "")
        if key != settings.gas_api_key:
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

        return await call_next(request)
