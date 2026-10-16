"""Concurrency tests to verify race-condition protection on limited inventory."""
from concurrent.futures import ThreadPoolExecutor
from app.models import Book, Reservation
from app.database import SessionLocal


def test_concurrent_reservations_cannot_exceed_inventory(client, db_session):
    """
    Test that concurrent reservation attempts do not result in race conditions.
    When a book has 2 copies and 8 concurrent requests arrive, exactly 2 succeed
    and 6 fail, leaving available_copies == 0 and exactly 2 active reservations.
    """
    book = Book(title="Distributed Algorithms", author="Nancy Lynch", total_copies=2, available_copies=2)
    db_session.add(book)
    db_session.commit()
    book_id = book.id

    def attempt_reservation(user_idx):
        return client.post(
            f"/books/{book_id}/reserve",
            json={"user_name": f"concurrent_user_{user_idx}"},
        )

    # Launch 8 concurrent requests
    with ThreadPoolExecutor(max_workers=8) as executor:
        responses = list(executor.map(attempt_reservation, range(8)))

    successes = [r for r in responses if r.status_code == 201]
    failures = [r for r in responses if r.status_code == 400]

    assert len(successes) == 2, f"Expected exactly 2 successes, got {len(successes)}"
    assert len(failures) == 6, f"Expected exactly 6 failures, got {len(failures)}"

    # Check database state
    db_session.expire_all()
    final_book = db_session.query(Book).filter(Book.id == book_id).first()
    assert final_book.available_copies == 0

    active_reservations = (
        db_session.query(Reservation)
        .filter(Reservation.book_id == book_id, Reservation.status == "active")
        .count()
    )
    assert active_reservations == 2
