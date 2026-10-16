"""Comprehensive tests for reservation business logic, expirations, cancellations, and constraints."""
from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy.exc import IntegrityError
from app.models import Book, Reservation


def test_reserve_book_success(client, db_session):
    """Test successful reservation decrements available copies and sets 7-day expiration."""
    book = Book(title="System Design", author="Alex Xu", total_copies=3, available_copies=3)
    db_session.add(book)
    db_session.commit()

    before_time = datetime.now(timezone.utc)
    res = client.post(f"/books/{book.id}/reserve", json={"user_name": "carol_danvers"})
    assert res.status_code == 201
    data = res.json()
    assert data["book_id"] == book.id
    assert data["user_name"] == "carol_danvers"
    assert data["status"] == "active"

    # Verify 7-day expiration window
    created_at = datetime.fromisoformat(data["reservation_date"])
    expires_at = datetime.fromisoformat(data["expires_at"])
    delta = expires_at - created_at
    assert abs(delta.total_seconds() - (7 * 86400)) < 5

    # Verify database state
    db_session.expire_all()
    db_book = db_session.query(Book).filter(Book.id == book.id).first()
    assert db_book.available_copies == 2


def test_reserve_book_exhausted_inventory(client, db_session):
    """Test that reserving beyond available inventory fails with HTTP 400 without corrupting counts."""
    book = Book(title="Domain-Driven Design", author="Eric Evans", total_copies=2, available_copies=2)
    db_session.add(book)
    db_session.commit()

    # Reserve 1st copy
    r1 = client.post(f"/books/{book.id}/reserve", json={"user_name": "user_one"})
    assert r1.status_code == 201

    # Reserve 2nd copy (inventory now exhausted)
    r2 = client.post(f"/books/{book.id}/reserve", json={"user_name": "user_two"})
    assert r2.status_code == 201

    # 3rd reservation attempt MUST fail
    r3 = client.post(f"/books/{book.id}/reserve", json={"user_name": "user_three"})
    assert r3.status_code == 400
    assert "No copies available for reservation" in r3.json()["detail"]

    # Database inventory must remain at 0, not negative
    db_session.expire_all()
    db_book = db_session.query(Book).filter(Book.id == book.id).first()
    assert db_book.available_copies == 0

    active_count = db_session.query(Reservation).filter(Reservation.book_id == book.id, Reservation.status == "active").count()
    assert active_count == 2


def test_single_copy_boundary_case(client, db_session):
    """Test boundary condition for a book with total_copies=1."""
    book = Book(title="Single Copy Rare Book", author="Archivist", total_copies=1, available_copies=1)
    db_session.add(book)
    db_session.commit()

    # 1. Reserve the only copy
    r1 = client.post(f"/books/{book.id}/reserve", json={"user_name": "first_reader"})
    assert r1.status_code == 201
    res_id = r1.json()["id"]

    db_session.expire_all()
    assert db_session.query(Book).filter(Book.id == book.id).first().available_copies == 0

    # 2. Second request rejected
    r2 = client.post(f"/books/{book.id}/reserve", json={"user_name": "second_reader"})
    assert r2.status_code == 400

    # 3. Cancel first reservation restores the copy
    rc = client.delete(f"/reservations/{res_id}")
    assert rc.status_code == 200
    assert rc.json()["status"] == "cancelled"

    db_session.expire_all()
    assert db_session.query(Book).filter(Book.id == book.id).first().available_copies == 1

    # 4. Now second reader can reserve
    r3 = client.post(f"/books/{book.id}/reserve", json={"user_name": "second_reader"})
    assert r3.status_code == 201
    db_session.expire_all()
    assert db_session.query(Book).filter(Book.id == book.id).first().available_copies == 0


def test_reserve_validation_and_not_found(client):
    """Test reservation validation and non-existent book handling."""
    # 404 for non-existent book
    res = client.post("/books/9999/reserve", json={"user_name": "ghost_user"})
    assert res.status_code == 404

    # 422 for empty username
    res = client.post("/books/1/reserve", json={"user_name": ""})
    assert res.status_code == 422

    # 422 for whitespace username
    res = client.post("/books/1/reserve", json={"user_name": "   "})
    assert res.status_code == 422


def test_cancel_reservation_success(client, db_session):
    """Test cancelling an active reservation restores exactly one copy."""
    book = Book(title="Concurrency in Go", author="Katherine Cox-Buday", total_copies=3, available_copies=3)
    db_session.add(book)
    db_session.commit()

    res = client.post(f"/books/{book.id}/reserve", json={"user_name": "golang_fan"})
    assert res.status_code == 201
    res_id = res.json()["id"]

    db_session.expire_all()
    assert db_session.query(Book).filter(Book.id == book.id).first().available_copies == 2

    # Cancel reservation
    cancel_res = client.delete(f"/reservations/{res_id}")
    assert cancel_res.status_code == 200
    data = cancel_res.json()
    assert data["id"] == res_id
    assert data["status"] == "cancelled"

    # Inventory restored
    db_session.expire_all()
    db_book = db_session.query(Book).filter(Book.id == book.id).first()
    assert db_book.available_copies == 3


def test_repeated_cancellation_prevents_double_restoration(client, db_session):
    """CRITICAL RULE: Repeated cancellation must not restore extra copies."""
    book = Book(title="Security Engineering", author="Ross Anderson", total_copies=2, available_copies=2)
    db_session.add(book)
    db_session.commit()

    # Reserve
    r = client.post(f"/books/{book.id}/reserve", json={"user_name": "sec_researcher"})
    res_id = r.json()["id"]

    db_session.expire_all()
    assert db_session.query(Book).filter(Book.id == book.id).first().available_copies == 1

    # First cancellation: succeeds
    c1 = client.delete(f"/reservations/{res_id}")
    assert c1.status_code == 200

    db_session.expire_all()
    assert db_session.query(Book).filter(Book.id == book.id).first().available_copies == 2

    # Second cancellation: MUST fail
    c2 = client.delete(f"/reservations/{res_id}")
    assert c2.status_code == 400
    assert "already cancelled" in c2.json()["detail"]

    # Verify inventory was NOT incremented to 3!
    db_session.expire_all()
    assert db_session.query(Book).filter(Book.id == book.id).first().available_copies == 2


def test_cancel_nonexistent_reservation(client):
    """Test cancelling non-existent reservation returns 404."""
    res = client.delete("/reservations/88888")
    assert res.status_code == 404
    assert "Reservation with ID 88888 not found" in res.json()["detail"]


def test_deterministic_expiration_restores_copy_once(client, db_session):
    """
    CRITICAL RULE:
    - Expiration automatically restores copy before availability checks.
    - Expiration restores copy EXACTLY ONCE.
    - Repeated checks do not double restore.
    - Expired reservations cannot be cancelled.
    """
    book = Book(title="Operating Systems: Three Easy Pieces", author="Arpaci-Dusseau", total_copies=2, available_copies=2)
    db_session.add(book)
    db_session.commit()

    # Reserve copy -> available becomes 1
    r = client.post(f"/books/{book.id}/reserve", json={"user_name": "kernel_dev"})
    res_id = r.json()["id"]

    db_session.expire_all()
    assert db_session.query(Book).filter(Book.id == book.id).first().available_copies == 1

    # Deterministically expire this reservation by modifying expires_at in DB to 2 days in the past
    past_time = datetime.now(timezone.utc) - timedelta(days=2)
    db_res = db_session.query(Reservation).filter(Reservation.id == res_id).first()
    db_res.expires_at = past_time
    db_session.commit()

    # Now make an availability check via GET /books/
    list_res = client.get("/books/")
    assert list_res.status_code == 200

    # Verify the book copy was automatically restored to 2
    db_session.expire_all()
    db_book = db_session.query(Book).filter(Book.id == book.id).first()
    assert db_book.available_copies == 2

    # Verify the reservation status transitioned to 'expired'
    refreshed_res = db_session.query(Reservation).filter(Reservation.id == res_id).first()
    assert refreshed_res.status == "expired"

    # Repeated availability check: available_copies must remain 2 (NEVER 3)
    client.get("/books/")
    client.get(f"/books/{book.id}")
    db_session.expire_all()
    assert db_session.query(Book).filter(Book.id == book.id).first().available_copies == 2

    # Attempt to cancel expired reservation: MUST fail with 400
    cancel_res = client.delete(f"/reservations/{res_id}")
    assert cancel_res.status_code == 400
    assert "already expired" in cancel_res.json()["detail"]

    # Verify inventory is still 2
    db_session.expire_all()
    assert db_session.query(Book).filter(Book.id == book.id).first().available_copies == 2


def test_database_check_constraints_enforced(db_session):
    """Test that SQLite check constraints prevent negative or overflow inventory."""
    # Test 1: available_copies cannot be negative
    invalid_book_neg = Book(title="Bad Book Neg", author="Author", total_copies=2, available_copies=-1)
    db_session.add(invalid_book_neg)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # Test 2: available_copies cannot exceed total_copies
    invalid_book_overflow = Book(title="Bad Book Overflow", author="Author", total_copies=2, available_copies=3)
    db_session.add(invalid_book_overflow)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()

    # Test 3: total_copies must be > 0
    invalid_book_zero = Book(title="Bad Book Zero", author="Author", total_copies=0, available_copies=0)
    db_session.add(invalid_book_zero)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_list_reservations_endpoint(client, db_session):
    """Test listing reservations and filtering."""
    book = Book(title="Rust in Action", author="Tim McNamara", total_copies=5, available_copies=5)
    db_session.add(book)
    db_session.commit()

    r1 = client.post(f"/books/{book.id}/reserve", json={"user_name": "ferris"})
    r2 = client.post(f"/books/{book.id}/reserve", json={"user_name": "crab"})
    assert r1.status_code == 201
    assert r2.status_code == 201

    res = client.get("/reservations/")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2
    assert data[0]["book_title"] == "Rust in Action"

    # Filter by status
    res_active = client.get("/reservations/?status=active")
    assert res_active.status_code == 200
    assert len(res_active.json()) == 2

    res_cancelled = client.get("/reservations/?status=cancelled")
    assert res_cancelled.status_code == 200
    assert len(res_cancelled.json()) == 0
