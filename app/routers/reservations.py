"""Router for reservation management and cancellations."""
from typing import List, Optional
from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ReservationResponse, ErrorResponse
from app.services import cancel_reservation, get_all_reservations

router = APIRouter(prefix="/reservations", tags=["Reservations"])


@router.get(
    "/",
    response_model=List[ReservationResponse],
    status_code=status.HTTP_200_OK,
    operation_id="list_reservations",
    summary="List all reservations",
    description="Retrieve all reservations with optional filtering by status (active, cancelled, expired) or book_id. Automatically updates expired statuses.",
)
def retrieve_all_reservations(
    book_id: Optional[int] = Query(None, description="Optional book ID filter"),
    reservation_status: Optional[str] = Query(None, alias="status", description="Optional status filter: active, cancelled, expired"),
    db: Session = Depends(get_db),
) -> List[ReservationResponse]:
    """Retrieve reservations."""
    return get_all_reservations(db, book_id=book_id, reservation_status=reservation_status)


@router.delete(
    "/{reservation_id}",
    response_model=ReservationResponse,
    status_code=status.HTTP_200_OK,
    operation_id="cancel_reservation",
    summary="Cancel a reservation",
    description="Cancel an active reservation. Restores exactly 1 copy to the book's inventory. Fails if already cancelled or expired.",
    responses={
        400: {"model": ErrorResponse, "description": "Reservation is already cancelled or expired"},
        404: {"model": ErrorResponse, "description": "Reservation not found"},
    },
)
def cancel_existing_reservation(
    reservation_id: int = Path(..., description="Unique integer ID of the reservation", ge=1),
    db: Session = Depends(get_db),
) -> ReservationResponse:
    """Cancel an active reservation."""
    return cancel_reservation(db, reservation_id=reservation_id)
