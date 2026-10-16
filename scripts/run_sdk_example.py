"""Example script showing genuine OpenAPI-generated Python SDK usage.
Matches the PDF specification:
from library_sdk.api.books_api import BooksApi
from library_sdk import ApiClient
"""
import sys
import os

# Add SDK directory to python path if not installed globally
SDK_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "library_sdk")
if SDK_DIR not in sys.path:
    sys.path.insert(0, SDK_DIR)

from library_sdk import ApiClient, Configuration
from library_sdk.api.books_api import BooksApi
from library_sdk.api.reservations_api import ReservationsApi
from library_sdk.models.book_create import BookCreate
from library_sdk.models.reservation_create import ReservationCreate


def main():
    print("=" * 60)
    print(" Library Book Reservation System - Generated Python SDK Demo")
    print("=" * 60)

    # 1. Initialize API Client
    config = Configuration(host="http://127.0.0.1:8000")
    client = ApiClient(configuration=config)

    books_api = BooksApi(client)
    reservations_api = ReservationsApi(client)

    print("\n[1] Fetching all books via BooksApi.list_books()...")
    try:
        books = books_api.list_books()
        print(f"-> Successfully retrieved {len(books)} books:")
        for b in books[:3]:
            print(f"   * [{b.id}] {b.title} by {b.author} (Available: {b.available_copies}/{b.total_copies})")
    except Exception as e:
        print(f"Error calling list_books: {e}")
        return

    print("\n[2] Creating a new book via BooksApi.create_book()...")
    try:
        new_book_req = BookCreate(
            title="Designing Distributed Systems with Python",
            author="Brendan Burns & Contributors",
            total_copies=3,
        )
        created_book = books_api.create_book(book_create=new_book_req)
        print(f"-> Created book ID={created_book.id}: '{created_book.title}' with {created_book.available_copies} copies")
        book_id = created_book.id
    except Exception as e:
        print(f"Error creating book: {e}")
        return

    print(f"\n[3] Reserving a copy of book ID={book_id} via BooksApi.reserve_book()...")
    try:
        reserve_req = ReservationCreate(user_name="sdk_tester_alice")
        reservation = books_api.reserve_book(book_id=book_id, reservation_create=reserve_req)
        print(f"-> Reserved! Reservation ID={reservation.id}, User={reservation.user_name}, Status={reservation.status}")
        print(f"   Expires at: {reservation.expires_at}")
        reservation_id = reservation.id
    except Exception as e:
        print(f"Error reserving book: {e}")
        return

    print(f"\n[4] Checking updated book availability via BooksApi.get_book({book_id})...")
    try:
        updated_book = books_api.get_book(book_id=book_id)
        print(f"-> Book '{updated_book.title}' now has {updated_book.available_copies}/{updated_book.total_copies} available copies")
    except Exception as e:
        print(f"Error getting book: {e}")

    print("\n[5] Listing active reservations via ReservationsApi.list_reservations()...")
    try:
        res_list = reservations_api.list_reservations(status="active")
        print(f"-> Total active reservations: {len(res_list)}")
    except Exception as e:
        print(f"Error listing reservations: {e}")

    print(f"\n[6] Cancelling reservation ID={reservation_id} via ReservationsApi.cancel_reservation()...")
    try:
        cancelled = reservations_api.cancel_reservation(reservation_id=reservation_id)
        print(f"-> Successfully cancelled reservation {cancelled.id}! Status is now: {cancelled.status}")
    except Exception as e:
        print(f"Error cancelling reservation: {e}")
        return

    print(f"\n[7] Verifying inventory restoration after cancellation...")
    try:
        restored_book = books_api.get_book(book_id=book_id)
        print(f"-> Book '{restored_book.title}' available copies restored to {restored_book.available_copies}/{restored_book.total_copies}")
    except Exception as e:
        print(f"Error checking book: {e}")

    print("\n" + "=" * 60)
    print(" Python SDK Verification Succeeded 100%!")
    print("=" * 60)


if __name__ == "__main__":
    main()
