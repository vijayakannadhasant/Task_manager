"""Smoke tests for the OpenAPI-generated Python SDK using real HTTP calls."""
import socket
import threading
import time
import pytest
import uvicorn

import sys
import os
SDK_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "library_sdk")
if SDK_DIR not in sys.path:
    sys.path.insert(0, SDK_DIR)

from library_sdk import ApiClient, Configuration
from library_sdk.api.books_api import BooksApi
from library_sdk.api.reservations_api import ReservationsApi
from library_sdk.models.book_create import BookCreate
from library_sdk.models.reservation_create import ReservationCreate
from app.main import app


def get_free_port():
    """Find an available port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def live_server():
    """Start uvicorn server in a background thread for genuine HTTP SDK calls."""
    port = get_free_port()
    config = uvicorn.Config(app=app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    # Wait for server to start
    start_time = time.time()
    while not server.started:
        time.sleep(0.05)
        if time.time() - start_time > 5:
            raise RuntimeError("Uvicorn test server failed to start within 5s")

    base_url = f"http://127.0.0.1:{port}"
    yield base_url

    server.should_exit = True
    thread.join(timeout=2)


def test_sdk_full_workflow_smoke(live_server):
    """Verify that the generated Python SDK functions correctly with real HTTP requests."""
    config = Configuration(host=live_server)
    client = ApiClient(configuration=config)

    books_api = BooksApi(client)
    reservations_api = ReservationsApi(client)

    # 1. Create a book via SDK
    new_book = BookCreate(
        title="Site Reliability Engineering with SDK",
        author="Google SRE Team",
        total_copies=2,
    )
    created = books_api.create_book(book_create=new_book)
    assert created.id is not None
    assert created.title == "Site Reliability Engineering with SDK"
    assert created.available_copies == 2
    book_id = created.id

    # 2. Retrieve book by ID
    retrieved = books_api.get_book(book_id=book_id)
    assert retrieved.id == book_id
    assert retrieved.available_copies == 2

    # 3. Reserve a copy
    res_req = ReservationCreate(user_name="sre_engineer")
    reservation = books_api.reserve_book(book_id=book_id, reservation_create=res_req)
    assert reservation.id is not None
    assert reservation.book_id == book_id
    assert reservation.user_name == "sre_engineer"
    assert reservation.status == "active"
    reservation_id = reservation.id

    # 4. Check available copies decremented
    updated_book = books_api.get_book(book_id=book_id)
    assert updated_book.available_copies == 1

    # 5. List reservations
    res_list = reservations_api.list_reservations(status="active")
    assert any(r.id == reservation_id for r in res_list)

    # 6. Cancel reservation
    cancelled = reservations_api.cancel_reservation(reservation_id=reservation_id)
    assert cancelled.id == reservation_id
    assert cancelled.status == "cancelled"

    # 7. Check inventory restored
    restored_book = books_api.get_book(book_id=book_id)
    assert restored_book.available_copies == 2
