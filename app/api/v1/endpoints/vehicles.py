from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.crud import customer as customer_crud
from app.crud import vehicle as vehicle_crud
from app.db.models.user import User
from app.schemas.vehicle import (
    VehicleCreate,
    VehicleResponse,
    VehicleUpdate,
)


router = APIRouter(
    prefix="/vehicles",
    tags=["Vehicles"],
)


def get_current_customer_id(
    db: Session,
    current_user: User,
) -> int:
    """Get the customer profile ID for a customer user."""

    customer = customer_crud.get_customer_by_user_id(
        db,
        current_user.id,
    )

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found",
        )

    return customer.id


@router.get(
    "",
    response_model=list[VehicleResponse],
)
def list_vehicles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[VehicleResponse]:

    if current_user.role == "CUSTOMER":
        customer_id = get_current_customer_id(
            db,
            current_user,
        )

        vehicles = vehicle_crud.get_customer_vehicles(
            db,
            customer_id,
        )

    elif current_user.role in {
        "ADMIN",
        "SERVICE_ADVISOR",
        "TECHNICIAN",
    }:
        vehicles = vehicle_crud.get_vehicles(db)

    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    return [
        VehicleResponse.model_validate(vehicle)
        for vehicle in vehicles
    ]


@router.post(
    "",
    response_model=VehicleResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_vehicle(
    request: VehicleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> VehicleResponse:

    customer_id = request.customer_id

    if current_user.role == "CUSTOMER":
        own_customer_id = get_current_customer_id(
            db,
            current_user,
        )

        if customer_id != own_customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only create vehicles for yourself",
            )

    elif current_user.role not in {
        "ADMIN",
        "SERVICE_ADVISOR",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    customer = customer_crud.get_customer(
        db,
        customer_id,
    )

    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found",
        )

    try:
        vehicle = vehicle_crud.create_vehicle(
            db,
            customer_id=request.customer_id,
            registration_no=request.registration_no,
            make=request.make,
            model=request.model,
            year=request.year,
            details=request.details,
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Vehicle registration number already exists",
        ) from None

    return VehicleResponse.model_validate(vehicle)


@router.get(
    "/{vehicle_id}",
    response_model=VehicleResponse,
)
def get_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> VehicleResponse:

    vehicle = vehicle_crud.get_vehicle(db, vehicle_id)

    if vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )

    if current_user.role == "CUSTOMER":
        customer_id = get_current_customer_id(
            db,
            current_user,
        )

        if vehicle.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your own vehicles",
            )

    elif current_user.role not in {
        "ADMIN",
        "SERVICE_ADVISOR",
        "TECHNICIAN",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    return VehicleResponse.model_validate(vehicle)


@router.put(
    "/{vehicle_id}",
    response_model=VehicleResponse,
)
def update_vehicle(
    vehicle_id: int,
    request: VehicleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> VehicleResponse:

    vehicle = vehicle_crud.get_vehicle(db, vehicle_id)

    if vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )

    if current_user.role == "CUSTOMER":
        customer_id = get_current_customer_id(
            db,
            current_user,
        )

        if vehicle.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own vehicles",
            )

    elif current_user.role not in {
        "ADMIN",
        "SERVICE_ADVISOR",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    try:
        vehicle = vehicle_crud.update_vehicle(
            db,
            vehicle,
            registration_no=request.registration_no,
            make=request.make,
            model=request.model,
            year=request.year,
            details=request.details,
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Vehicle registration number already exists",
        ) from None

    return VehicleResponse.model_validate(vehicle)


@router.delete(
    "/{vehicle_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:

    vehicle = vehicle_crud.get_vehicle(db, vehicle_id)

    if vehicle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found",
        )

    if current_user.role == "CUSTOMER":
        customer_id = get_current_customer_id(
            db,
            current_user,
        )

        if vehicle.customer_id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own vehicles",
            )

    elif current_user.role not in {
        "ADMIN",
        "SERVICE_ADVISOR",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    vehicle_crud.delete_vehicle(db, vehicle)