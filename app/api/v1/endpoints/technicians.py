from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.crud import technician as technician_crud
from app.crud import user as user_crud
from app.db.models.user import User
from app.schemas.technician import (
    TechnicianCreate,
    TechnicianResponse,
    TechnicianUpdate,
)


router = APIRouter(
    prefix="/technicians",
    tags=["Technicians"],
)


@router.get(
    "",
    response_model=list[TechnicianResponse],
)
def list_technicians(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[TechnicianResponse]:

    if current_user.role not in {
        "ADMIN",
        "SERVICE_ADVISOR",
        "TECHNICIAN",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    technicians = technician_crud.get_technicians(db)

    return [
        TechnicianResponse.model_validate(technician)
        for technician in technicians
    ]


@router.post(
    "",
    response_model=TechnicianResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_technician(
    request: TechnicianCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TechnicianResponse:

    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can create technicians",
        )

    user = user_crud.get_user(db, request.user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.role != "TECHNICIAN":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must have TECHNICIAN role",
        )

    existing = db.scalar(
        select(
            technician_crud.Technician
            if hasattr(technician_crud, "Technician")
            else User
        )
    ) if False else None

    try:
        technician = technician_crud.create_technician(
            db,
            user_id=request.user_id,
            specialities=request.specialities,
            is_active=request.is_active,
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Technician profile already exists for this user",
        ) from None

    return TechnicianResponse.model_validate(technician)


@router.get(
    "/{technician_id}",
    response_model=TechnicianResponse,
)
def get_technician(
    technician_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TechnicianResponse:

    if current_user.role not in {
        "ADMIN",
        "SERVICE_ADVISOR",
        "TECHNICIAN",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    technician = technician_crud.get_technician(
        db,
        technician_id,
    )

    if technician is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Technician not found",
        )

    return TechnicianResponse.model_validate(technician)


@router.put(
    "/{technician_id}",
    response_model=TechnicianResponse,
)
def update_technician(
    technician_id: int,
    request: TechnicianUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TechnicianResponse:

    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can update technicians",
        )

    technician = technician_crud.get_technician(
        db,
        technician_id,
    )

    if technician is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Technician not found",
        )

    try:
        technician = technician_crud.update_technician(
            db,
            technician,
            specialities=request.specialities,
            is_active=request.is_active,
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Technician could not be updated",
        ) from None

    return TechnicianResponse.model_validate(technician)


@router.delete(
    "/{technician_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_technician(
    technician_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:

    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can delete technicians",
        )

    technician = technician_crud.get_technician(
        db,
        technician_id,
    )

    if technician is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Technician not found",
        )

    technician_crud.delete_technician(db, technician)