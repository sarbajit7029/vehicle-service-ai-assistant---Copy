from fastapi import APIRouter
from app.api.v1.endpoints import documents
from app.api.v1.endpoints import bookings
from app.api.v1.endpoints import (
    auth,
    customers,
    service_types,
    technicians,
    users,
    vehicles,
)


api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(customers.router)
api_router.include_router(vehicles.router)
api_router.include_router(service_types.router)
api_router.include_router(technicians.router)
api_router.include_router(bookings.router)
api_router.include_router(documents.router)