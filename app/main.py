from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.endpoints import (
    auth,
    bookings,
    chat,
    customers,
    documents,
    service_types,
    technicians,
    users,
    vehicles,
)

from app.core.config import settings
from app.websocket.chat_handler import router as websocket_chat_router


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)


# =========================================================
# STATIC FILES
# =========================================================

BASE_DIR = Path(__file__).resolve().parent

STATIC_DIR = BASE_DIR / "static"

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)


# =========================================================
# FRONTEND
# =========================================================

@app.get("/", include_in_schema=False)
def frontend():
    return FileResponse(
        STATIC_DIR / "chat.html"
    )


# =========================================================
# HEALTH
# =========================================================

@app.get(
    "/health",
    tags=["Health"],
)
def health_check():

    return {
        "status": "ok",
        "service": settings.app_name,
    }


# =========================================================
# REST API ROUTES
# =========================================================

app.include_router(
    auth.router,
    prefix="/api/v1",
)

app.include_router(
    users.router,
    prefix="/api/v1",
)

app.include_router(
    customers.router,
    prefix="/api/v1",
)

app.include_router(
    vehicles.router,
    prefix="/api/v1",
)

app.include_router(
    service_types.router,
    prefix="/api/v1",
)

app.include_router(
    technicians.router,
    prefix="/api/v1",
)

app.include_router(
    bookings.router,
    prefix="/api/v1",
)

app.include_router(
    documents.router,
    prefix="/api/v1",
)

app.include_router(
    chat.router,
    prefix="/api/v1",
)


# =========================================================
# WEBSOCKET
# =========================================================

app.include_router(
    websocket_chat_router
)