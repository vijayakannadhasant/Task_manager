"""Business logic services for library operations, inventory management, and reservations."""
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy import update
from sqlalchemy.orm import Session
from app.models import Book, Reservation
from app.schemas import BookCreate


def utc_now() -> datetime:
    """Return timezone-aware current UTC datetime."""
    return datetime.now(timezone.utc)


def ensure_utc(dt: datetime) -> datetime:
    """Ensure datetime is timezone-aware in UTC."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def process_expired_reservations(db: Session, target_time: Optional[datetime] = None) -> int:
    """
    Process any active reservations that have passed their expires_at timestamp.
    - Transitions reservation status to 'expired'.
    - Restores exactly 1 copy to the book's available_copies (never exceeding total_copies).
    - Idempotent: once marked expired, subsequent invocations will not process them again.
    Returns the count of expired reservations processed.
    """
    now = ensure_utc(target_time or utc_now())

    # Query active reservations
    active_reservations = (
        db.query(Reservation)
        .filter(Reservation.status == "active")
        .all()
    )

    if not active_reservations:
        return 0

    count = 0
    for res in active_reservations:
        if ensure_utc(res.expires_at) <= now:
            res.status = "expired"
            book = db.query(Book).filter(Book.id == res.book_id).first()
            if book:
                if book.available_copies < book.total_copies:
                    book.available_copies += 1
            count += 1

    if count > 0:
        db.commit()
    return count


def create_book(db: Session, book_in: BookCreate) -> Book:
    """Create a new book with available_copies initialized to total_copies."""
    book = Book(
        title=book_in.title,
        author=book_in.author,
        total_copies=book_in.total_copies,
        available_copies=book_in.total_copies,
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def get_all_books(db: Session, target_time: Optional[datetime] = None) -> List[Book]:
    """Retrieve all books after processing expired reservations."""
    process_expired_reservations(db, target_time=target_time)
    return db.query(Book).order_by(Book.id.asc()).all()


def get_book_by_id(db: Session, book_id: int, target_time: Optional[datetime] = None) -> Book:
    """Retrieve a single book by ID after processing expired reservations."""
    process_expired_reservations(db, target_time=target_time)
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found",
        )
    return book


def reserve_book(
    db: Session,
    book_id: int,
    user_name: str,
    expiration_days: int = 7,
    now: Optional[datetime] = None,
) -> Reservation:
    """
    Reserve an available book copy for a user.
    - Processes any pending expired reservations first.
    - Atomically decrements available_copies only if available_copies > 0.
    - Fails with HTTP 400 if no copies remain.
    - Sets expires_at to reservation_date + expiration_days.
    """
    current_time = ensure_utc(now or utc_now())

    # Step 1: Process expirations
    process_expired_reservations(db, target_time=current_time)

    # Step 2: Check book exists
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found",
        )

    # Step 3: Check availability
    if book.available_copies <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No copies available for reservation",
        )

    # Step 4: Atomic conditional update
    stmt = (
        update(Book)
        .where(Book.id == book_id, Book.available_copies > 0)
        .values(available_copies=Book.available_copies - 1)
    )
    result = db.execute(stmt)
    if result.rowcount == 0:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No copies available for reservation",
        )

    # Step 5: Insert reservation
    expires_at = current_time + timedelta(days=expiration_days)
    reservation = Reservation(
        book_id=book_id,
        user_name=user_name,
        reservation_date=current_time,
        expires_at=expires_at,
        status="active",
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)

    reservation.book_title = book.title
    return reservation


def cancel_reservation(
    db: Session,
    reservation_id: int,
    now: Optional[datetime] = None,
) -> Reservation:
    """
    Cancel an active reservation.
    - Restores exactly 1 copy to the book's inventory.
    - Fails if already cancelled (prevents double restoration).
    - Fails if expired (prevents restoring copies after expiration).
    - Fails with 404 if reservation does not exist.
    """
    current_time = ensure_utc(now or utc_now())

    # Step 1: Process expired reservations first
    process_expired_reservations(db, target_time=current_time)

    # Step 2: Retrieve reservation
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reservation with ID {reservation_id} not found",
        )

    # Step 3: Validate status
    if reservation.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reservation is already cancelled",
        )

    if reservation.status == "expired":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reservation has already expired and cannot be cancelled",
        )

    if ensure_utc(reservation.expires_at) <= current_time:
        reservation.status = "expired"
        book = db.query(Book).filter(Book.id == reservation.book_id).first()
        if book and book.available_copies < book.total_copies:
            book.available_copies += 1
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reservation has already expired and cannot be cancelled",
        )

    # Step 4: Mark cancelled and restore copy
    reservation.status = "cancelled"
    stmt = (
        update(Book)
        .where(Book.id == reservation.book_id, Book.available_copies < Book.total_copies)
        .values(available_copies=Book.available_copies + 1)
    )
    db.execute(stmt)
    db.commit()
    db.refresh(reservation)

    if reservation.book:
        reservation.book_title = reservation.book.title
    return reservation


def get_all_reservations(
    db: Session,
    book_id: Optional[int] = None,
    reservation_status: Optional[str] = None,
    target_time: Optional[datetime] = None,
) -> List[Reservation]:
    """Retrieve reservations with optional filtering by book_id and status."""
    process_expired_reservations(db, target_time=target_time)

    query = db.query(Reservation).order_by(Reservation.id.desc())
    if book_id is not None:
        query = query.filter(Reservation.book_id == book_id)
    if reservation_status is not None:
        query = query.filter(Reservation.status == reservation_status)

    reservations = query.all()
    for res in reservations:
        if res.book:
            res.book_title = res.book.title
    return reservations
