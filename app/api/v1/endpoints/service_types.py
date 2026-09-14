from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.crud import service_type as service_type_crud
from app.db.models.user import User
from app.schemas.service_type import (
    ServiceTypeCreate,
    ServiceTypeResponse,
    ServiceTypeUpdate,
)


router = APIRouter(
    prefix="/service-types",
    tags=["Service Types"],
)


@router.get(
    "",
    response_model=list[ServiceTypeResponse],
)
def list_service_types(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ServiceTypeResponse]:

    service_types = service_type_crud.get_service_types(db)

    return [
        ServiceTypeResponse.model_validate(service_type)
        for service_type in service_types
    ]


@router.post(
    "",
    response_model=ServiceTypeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_service_type(
    request: ServiceTypeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ServiceTypeResponse:

    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can create service types",
        )

    try:
        service_type = service_type_crud.create_service_type(
            db,
            name=request.name,
            description=request.description,
            base_price=request.base_price,
            duration_minutes=request.duration_minutes,
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Service type name already exists",
        ) from None

    return ServiceTypeResponse.model_validate(service_type)


@router.get(
    "/{service_type_id}",
    response_model=ServiceTypeResponse,
)
def get_service_type(
    service_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ServiceTypeResponse:

    service_type = service_type_crud.get_service_type(
        db,
        service_type_id,
    )

    if service_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service type not found",
        )

    return ServiceTypeResponse.model_validate(service_type)


@router.put(
    "/{service_type_id}",
    response_model=ServiceTypeResponse,
)
def update_service_type(
    service_type_id: int,
    request: ServiceTypeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ServiceTypeResponse:

    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can update service types",
        )

    service_type = service_type_crud.get_service_type(
        db,
        service_type_id,
    )

    if service_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service type not found",
        )

    try:
        service_type = service_type_crud.update_service_type(
            db,
            service_type,
            name=request.name,
            description=request.description,
            base_price=request.base_price,
            duration_minutes=request.duration_minutes,
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Service type name already exists",
        ) from None

    return ServiceTypeResponse.model_validate(service_type)


@router.delete(
    "/{service_type_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_service_type(
    service_type_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:

    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can delete service types",
        )

    service_type = service_type_crud.get_service_type(
        db,
        service_type_id,
    )

    if service_type is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service type not found",
        )

    service_type_crud.delete_service_type(db, service_type)