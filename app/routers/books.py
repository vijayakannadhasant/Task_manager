"""Router for book management and reservations."""
from typing import List
from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import (
    BookCreate,
    BookResponse,
    ReservationCreate,
    ReservationResponse,
    ErrorResponse,
)
from app.services import (
    create_book,
    get_all_books,
    get_book_by_id,
    reserve_book,
)

router = APIRouter(prefix="/books", tags=["Books"])


@router.post(
    "/",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_book",
    summary="Add a new book",
    description="Create a new book with specified title, author, and total copies.",
    responses={
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
)
def create_new_book(
    book_in: BookCreate,
    db: Session = Depends(get_db),
) -> BookResponse:
    """Create a new book entry in the library catalog."""
    return create_book(db, book_in)


@router.get(
    "/",
    response_model=List[BookResponse],
    status_code=status.HTTP_200_OK,
    operation_id="list_books",
    summary="Retrieve all books",
    description="List all books in the catalog along with up-to-date available copies. Automatically processes expired reservations before returning counts.",
)
def retrieve_all_books(
    db: Session = Depends(get_db),
) -> List[BookResponse]:
    """Retrieve all books with refreshed availability."""
    return get_all_books(db)


@router.get(
    "/{book_id}",
    response_model=BookResponse,
    status_code=status.HTTP_200_OK,
    operation_id="get_book",
    summary="Retrieve book details",
    description="Retrieve details of a specific book by ID, including current available copies.",
    responses={
        404: {"model": ErrorResponse, "description": "Book not found"},
    },
)
def retrieve_book_details(
    book_id: int = Path(..., description="Unique integer ID of the book", ge=1),
    db: Session = Depends(get_db),
) -> BookResponse:
    """Get single book details."""
    return get_book_by_id(db, book_id)


@router.post(
    "/{book_id}/reserve",
    response_model=ReservationResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="reserve_book",
    summary="Reserve a book copy",
    description="Reserve an available copy of a book for a named user. Decrements available copies by 1. Expires after 7 days.",
    responses={
        400: {"model": ErrorResponse, "description": "No copies available or invalid request"},
        404: {"model": ErrorResponse, "description": "Book not found"},
        422: {"model": ErrorResponse, "description": "Validation error"},
    },
)
def reserve_book_copy(
    book_id: int = Path(..., description="Unique integer ID of the book", ge=1),
    reservation_in: ReservationCreate = ...,
    db: Session = Depends(get_db),
) -> ReservationResponse:
    """Reserve a book copy for a user."""
    return reserve_book(db, book_id=book_id, user_name=reservation_in.user_name)
