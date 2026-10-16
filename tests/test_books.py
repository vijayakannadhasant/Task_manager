"""Unit and integration tests for Books endpoints."""
import pytest
from app.models import Book


def test_create_book_success(client, db_session):
    """Test creating a valid book."""
    payload = {
        "title": "Clean Architecture",
        "author": "Robert C. Martin",
        "total_copies": 5,
    }
    response = client.post("/books/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["title"] == "Clean Architecture"
    assert data["author"] == "Robert C. Martin"
    assert data["total_copies"] == 5
    assert data["available_copies"] == 5

    # Verify directly in test database
    db_book = db_session.query(Book).filter(Book.id == data["id"]).first()
    assert db_book is not None
    assert db_book.total_copies == 5
    assert db_book.available_copies == 5


@pytest.mark.parametrize(
    "invalid_payload,expected_status",
    [
        ({"title": "", "author": "Valid Author", "total_copies": 3}, 422),
        ({"title": "   ", "author": "Valid Author", "total_copies": 3}, 422),
        ({"title": "Valid Title", "author": "", "total_copies": 3}, 422),
        ({"title": "Valid Title", "author": "   ", "total_copies": 3}, 422),
        ({"title": "Valid Title", "author": "Valid Author", "total_copies": 0}, 422),
        ({"title": "Valid Title", "author": "Valid Author", "total_copies": -5}, 422),
        ({"author": "Missing Title", "total_copies": 3}, 422),
        ({"title": "Missing Total Copies", "author": "Valid Author"}, 422),
    ],
)
def test_create_book_validation(client, invalid_payload, expected_status):
    """Test book creation input validations."""
    response = client.post("/books/", json=invalid_payload)
    assert response.status_code == expected_status
    assert "detail" in response.json()


def test_list_books(client, db_session):
    """Test listing books returns all catalog items with up-to-date availability."""
    # List when empty
    res = client.get("/books/")
    assert res.status_code == 200
    assert res.json() == []

    # Insert two books
    b1 = Book(title="Book One", author="Author 1", total_copies=3, available_copies=3)
    b2 = Book(title="Book Two", author="Author 2", total_copies=2, available_copies=1)
    db_session.add_all([b1, b2])
    db_session.commit()

    res = client.get("/books/")
    assert res.status_code == 200
    books = res.json()
    assert len(books) == 2
    assert books[0]["title"] == "Book One"
    assert books[0]["available_copies"] == 3
    assert books[1]["title"] == "Book Two"
    assert books[1]["available_copies"] == 1


def test_get_book_by_id(client, db_session):
    """Test retrieving a book by its primary key ID."""
    book = Book(title="Refactoring", author="Martin Fowler", total_copies=4, available_copies=4)
    db_session.add(book)
    db_session.commit()

    res = client.get(f"/books/{book.id}")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == book.id
    assert data["title"] == "Refactoring"
    assert data["available_copies"] == 4


def test_get_book_not_found(client):
    """Test retrieving non-existent book returns 404."""
    res = client.get("/books/99999")
    assert res.status_code == 404
    assert "Book with ID 99999 not found" in res.json()["detail"]


def test_get_book_invalid_id(client):
    """Test invalid book ID format returns 422."""
    res = client.get("/books/abc")
    assert res.status_code == 422

    res = client.get("/books/0")
    assert res.status_code == 422
