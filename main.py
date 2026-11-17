from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from src.middleware.auth import ApiKeyMiddleware
from src.routes import kepengurusan, surat


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    yield
    print("Shutting down...")


app = FastAPI(lifespan=lifespan, root_path="/api")


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(title="TPKB GAS Server", version="1.0.0", routes=app.routes)
    schema.setdefault("components", {}).setdefault("securitySchemes", {})["ApiKeyAuth"] = {
        "type": "apiKey",
        "in": "header",
        "name": "X-API-Key",
    }
    for path in schema.get("paths", {}).values():
        for operation in path.values():
            operation.setdefault("security", [{"ApiKeyAuth": []}])
    app.openapi_schema = schema
    return schema


app.openapi = custom_openapi  # type: ignore


@app.exception_handler(RequestValidationError)
async def readable_validation_error(request: Request, exc: RequestValidationError):
    """Flatten FastAPI's validation error list into one sentence the frontend can show."""
    parts = []
    for err in exc.errors():
        field = ".".join(str(p) for p in err.get("loc", ()) if p != "body")
        parts.append(f"{field}: {err.get('msg', 'tidak valid')}" if field else err.get("msg", "tidak valid"))
    return JSONResponse(status_code=422, content={"detail": "Data tidak valid — " + "; ".join(parts)})

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "POST"],
    allow_headers=["X-API-Key"],
)

app.add_middleware(ApiKeyMiddleware)

app.include_router(kepengurusan.router)
app.include_router(surat.router)


@app.get("/ping")
async def ping():
    return {"message": "pong"}
