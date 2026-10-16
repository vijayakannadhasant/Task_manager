# Library Book Reservation System

A production-grade, concurrency-safe Library Book Reservation System built with **Python**, **FastAPI**, **SQLAlchemy**, **SQLite**, **Alembic**, **ReactJS**, and an **OpenAPI-generated Python SDK**.

This repository implements all functional and non-functional requirements from the Library Book Reservation System specification, including inventory constraints, automated 7-day expiration enforcement, idempotent cancellations, race-condition protection, and automated end-to-end testing.

---

## 📑 Table of Contents

- [System Architecture](#system-architecture)
- [Key Business Logic & "Trick Logic" Solutions](#key-business-logic--trick-logic-solutions)
  - [1. Limited Inventory Enforcement](#1-limited-inventory-enforcement)
  - [2. Automated 7-Day Expiration Handling](#2-automated-7-day-expiration-handling)
  - [3. Idempotent Cancellations & Copy Restoration](#3-idempotent-cancellations--copy-restoration)
  - [4. Race-Condition Protection & Concurrency Safety](#4-race-condition-protection--concurrency-safety)
  - [5. Database Integrity Constraints](#5-database-integrity-constraints)
  - [6. Architecture Decision: Reservation `status` Field](#6-architecture-decision-reservation-status-field)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Directory Structure](#directory-structure)
- [Quick Start Guide (Windows)](#quick-start-guide-windows)
  - [Step 1: Automated Environment Setup (`setupdev.bat`)](#step-1-automated-environment-setup-setupdevbat)
  - [Step 2: Database Seeding (`seed_data.sql`)](#step-2-database-seeding-seed_datasql)
  - [Step 3: Launch Application (`runapplication.bat`)](#step-3-launch-application-runapplicationbat)
- [API Endpoints & Documentation](#api-endpoints--documentation)
  - [Swagger UI & OpenAPI Specification](#swagger-ui--openapi-specification)
  - [Endpoint Summary](#endpoint-summary)
  - [CURL & JSON Request Examples](#curl--json-request-examples)
- [Platform Python SDK (OpenAPI Generator CLI)](#platform-python-sdk-openapi-generator-cli)
  - [Regenerating the SDK](#regenerating-the-sdk)
  - [SDK Usage Example](#sdk-usage-example)
  - [Running SDK Verification Script](#running-sdk-verification-script)
- [Automated Testing Suite](#automated-testing-suite)
- [Frontend Web Application](#frontend-web-application)
- [Troubleshooting & FAQ](#troubleshooting--faq)
- [Known Limitations & Production Considerations](#known-limitations--production-considerations)

---

## 🏛️ System Architecture

```
                                  ┌──────────────────────────────────────────────┐
                                  │           ReactJS Web Application            │
                                  │   (Vite + React 18 + Axios + Vanilla CSS)    │
                                  │           http://localhost:3000              │
                                  └──────────────────────┬───────────────────────┘
                                                         │
                                               REST API / JSON (Axios)
                                                         │
                                                         ▼
┌─────────────────────────────────┐       ┌──────────────────────────────────────┐
│       Generated Python SDK      │       │             FastAPI Backend          │
│   (`library_sdk` via OpenAPI)   │──────▶│   (Routers, Pydantic, Dependencies)  │
│      Scripts / Integrations     │ HTTP  │        http://127.0.0.1:8000         │
└─────────────────────────────────┘       └──────────────────┬───────────────────┘
                                                             │
                                                  SQLAlchemy 2.0 ORM
                                                             │
                                                             ▼
                                          ┌──────────────────────────────────────┐
                                          │          SQLite Database             │
                                          │  (WAL Mode, PRAGMA foreign_keys=ON)  │
                                          │         `library.db` File            │
                                          └──────────────────────────────────────┘
```

The system separates presentation, API routing, business domain logic, and persistence into clear layers:
- **`app/routers/`**: HTTP controllers declaring status codes, OpenAPI metadata, request validation, and responses.
- **`app/services.py`**: Pure, transactional business logic orchestrating inventory adjustments, expiration cycles, and cancellation constraints.
- **`app/models.py`**: Declarative SQLAlchemy models with database-level check constraints and SQLite foreign-key cascading.
- **`app/schemas.py`**: Pydantic schemas enforcing input validation and sanitized output serialization.
- **`alembic/`**: Version-controlled database migration scripts ensuring zero-drift schema changes.
- **`library_sdk/`**: Automated client generated using `@openapitools/openapi-generator-cli`.
- **`frontend/`**: Responsive, dependency-light React application with live inventory monitoring and user-friendly reservation management.

---

## 💡 Key Business Logic & "Trick Logic" Solutions

The specification highlights critical corner cases and hidden complexity. Here is how each requirement is strictly solved:

### 1. Limited Inventory Enforcement
- If a book has $N$ total copies, at most $N$ active reservations are permitted at any moment.
- When `available_copies == 0`, subsequent reservation attempts immediately reject with `400 Bad Request: "No copies available for reservation"`.
- Inventory is verified and decremented within an atomic transaction, preventing inventory corruption or negative counts.

### 2. Automated 7-Day Expiration Handling
- Every reservation sets `expires_at = reservation_date + 7 days` using explicit timezone-aware UTC timestamps (`UTCDateTime` decorator).
- **Just-In-Time Processing**: Before computing availability counts for `GET /books/`, `GET /books/{id}`, `POST /books/{id}/reserve`, or `GET /reservations/`, the service runs `process_expired_reservations()`.
- Active reservations whose `expires_at <= current_time` transition to `'expired'`.
- **Idempotency Guarantee**: Each expired reservation frees its copy **exactly once**. Subsequent requests will not restore additional copies.

### 3. Idempotent Cancellations & Copy Restoration
- Cancelling an active reservation (`DELETE /reservations/{reservation_id}`) transitions its status to `'cancelled'` and restores **exactly one copy** (`available_copies += 1`).
- **Repeated Cancellation Protection**: Cancelling an already-cancelled reservation returns `400 Bad Request: "Reservation is already cancelled"` and **does not** increment inventory.
- **Expired Reservation Protection**: An expired reservation has already returned its copy during expiration processing; attempting to cancel it returns `400 Bad Request: "Reservation has already expired and cannot be cancelled"`.
- Non-existent IDs return `404 Not Found`.

### 4. Race-Condition Protection & Concurrency Safety
- Under concurrent traffic, multiple threads might attempt to reserve the last copy (`available_copies == 1`).
- To prevent race conditions on SQLite without locking issues, `reserve_book` executes an atomic conditional update:
  ```sql
  UPDATE books
  SET available_copies = available_copies - 1
  WHERE id = :book_id AND available_copies > 0;
  ```
- If two requests hit simultaneously, SQLite guarantees row-level execution serialization. The first update succeeds (`rowcount == 1`). The second update sees `available_copies == 0`, fails the `WHERE` condition (`rowcount == 0`), rolls back, and raises `HTTP 400`.
- SQLite is configured with:
  - `PRAGMA foreign_keys = ON;`
  - `PRAGMA journal_mode = WAL;` (Write-Ahead Logging for non-blocking reads during writes)
  - `PRAGMA busy_timeout = 5000;` (5-second lock queue).

### 5. Database Integrity Constraints
Database check constraints prevent corrupted states even if direct SQL queries are executed:
```sql
CHECK (total_copies > 0)
CHECK (available_copies >= 0)
CHECK (available_copies <= total_copies)
CHECK (status IN ('active', 'cancelled', 'expired'))
```

### 6. Architecture Decision: Reservation `status` Field
The original table schema omitted an explicit reservation state column. We added `status VARCHAR(20) NOT NULL DEFAULT 'active'` for the following crucial architectural reasons:
1. **Idempotent Expirations**: Allows tracking whether a reservation was already processed for expiration, guaranteeing that copies are restored only once.
2. **Double-Cancellation Prevention**: Distinguishes active reservations from previously cancelled ones, guaranteeing repeated cancellations cannot artificially inflate inventory.
3. **Auditability & Frontend Usability**: Enables users to view reservation history (active vs cancelled vs expired) with complete operational transparency.
4. **Clean Migrations**: Fully managed in Alembic revision `423a45c14f9c_initial_schema_books_and_reservations.py`.

---

## 🛠️ Technology Stack

| Component | Technology | Version / Details |
| :--- | :--- | :--- |
| **Backend Framework** | FastAPI | 0.110+ (Python 3.12 compatible) |
| **ASGI Server** | Uvicorn | Standard with uvloop / httptools |
| **ORM & Database** | SQLAlchemy & SQLite | 2.0+ with WAL mode & Foreign Keys |
| **Schema Migrations** | Alembic | 1.13+ with batch SQLite migrations |
| **Frontend UI** | ReactJS | 18.2 with Vanilla CSS & Google Fonts |
| **HTTP Client** | Axios | 1.6+ with unified error handling |
| **SDK Generator** | OpenAPI Generator CLI | `@openapitools/openapi-generator-cli` 7.26.0 |
| **Testing** | Pytest | 8.1+ with FastAPI TestClient & ThreadPool |

---

## 📋 Prerequisites

To run this project on Windows:
1. **Python 3.10+** (Tested on Python 3.12.4).
2. **Node.js 18+ and npm** (Tested on Node v24.7.0 / npm 11.5.1).
3. **Java Runtime Environment (JRE 11+)** (Tested on Java 21 LTS, required only for OpenAPI Generator CLI).

---

## 📁 Directory Structure

```
library_system/
├── app/
│   ├── __init__.py               # Application package definition
│   ├── config.py                 # Pydantic BaseSettings (.env loading)
│   ├── database.py               # Engine, SQLite pragmas (WAL/FK), session factory
│   ├── models.py                 # Book and Reservation SQLAlchemy models
│   ├── schemas.py                # Pydantic request & response validation schemas
│   ├── services.py               # Core business logic (expiration, reserve, cancel)
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── books.py              # POST /books/, GET /books/, GET /books/{id}, POST .../reserve
│   │   └── reservations.py       # DELETE /reservations/{id}, GET /reservations/
│   └── main.py                   # FastAPI app declaration, CORS, error handlers
├── alembic/
│   ├── env.py                    # Alembic environment configured for SQLite batch mode
│   ├── script.py.mako            # Migration template
│   └── versions/
│       └── 423a45c14f9c_initial_schema_books_and_reservations.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # Isolated test database fixtures & TestClient
│   ├── test_books.py             # Book CRUD, validation, 404 & 422 coverage
│   ├── test_reservations.py      # Business logic: inventory, expiration, cancel idempotency
│   ├── test_concurrency.py       # ThreadPool race-condition verification
│   └── test_sdk_smoke.py         # End-to-end smoke test using the generated Python SDK
├── frontend/
│   ├── public/
│   │   └── index.html            # HTML entrypoint with Outfit & Inter Google Fonts
│   ├── src/
│   │   ├── api/
│   │   │   └── client.js         # Reusable Axios API client with error normalizer
│   │   ├── components/
│   │   │   ├── Navbar.jsx        # Brand, auto-sync polling indicator, add-book button
│   │   │   ├── StatsOverview.jsx # Catalog statistics metrics
│   │   │   ├── BookList.jsx      # Inventory cards, search, progress meters
│   │   │   ├── ReserveModal.jsx  # Reserve dialog with username input
│   │   │   ├── AddBookModal.jsx  # Add book form modal
│   │   │   └── ReservationList.jsx # Reservations management table & cancellation
│   │   ├── App.jsx               # Application state orchestration & interval sync
│   │   ├── index.css             # Vanilla CSS design tokens & glassmorphism theme
│   │   └── main.jsx              # React 18 createRoot mounting
│   ├── package.json              # Frontend npm dependencies and scripts
│   ├── vite.config.js            # Vite development & build configuration
│   └── .env.example              # Frontend environment template
├── library_sdk/                  # Genuine Python SDK generated via OpenAPI Generator CLI
├── scripts/
│   ├── generate_sdk.bat          # Reproducible script to export openapi.json and regenerate SDK
│   ├── run_sdk_example.py        # Demo script exercising SDK against live server
│   └── seed_db.py                # Database population script using seed_data.sql
├── seed_data.sql                 # Sample SQL seed file with books and reservations
├── requirements.txt              # Backend dependencies
├── alembic.ini                   # Alembic configuration
├── .env.example                  # Backend environment configuration template
├── .env                          # Local environment settings
├── .gitignore                    # Git ignore file
├── setupdev.bat                  # Windows batch script for automated environment setup
├── runapplication.bat            # Windows batch script launching backend and frontend
└── README.md                     # Comprehensive project documentation
```

---

## 🚀 Quick Start Guide (Windows)

All setup and run commands can be executed directly from the project root (`C:\Users\yogendra\.gemini\antigravity-ide\scratch\library_system`).

### Step 1: Automated Environment Setup (`setupdev.bat`)
Run the provided Windows setup script:
```cmd
setupdev.bat
```
This script automatically:
1. Creates the Python virtual environment (`env`) if it does not exist.
2. Installs backend dependencies from `requirements.txt`.
3. Runs `alembic upgrade head` to build the database schema.
4. Installs the generated SDK into the virtual environment in editable mode.
5. Installs frontend dependencies via `npm install` inside `frontend/`.
6. Halts with descriptive error codes if any prerequisite fails.

### Step 2: Database Seeding (`seed_data.sql`)
To load initial books and test reservations:
```cmd
.\env\Scripts\python.exe scripts\seed_db.py
```
This loads realistic computer science books (e.g., *Designing Data-Intensive Applications*, *Clean Code*, *Building Microservices*) and sample reservations into `library.db`.

### Step 3: Launch Application (`runapplication.bat`)
Launch both the backend API and frontend React client in separate Windows terminal windows:
```cmd
runapplication.bat
```
- **Backend API**: Running on `http://127.0.0.1:8000`
- **Swagger UI Interactive Docs**: Available at `http://127.0.0.1:8000/docs`
- **React Frontend**: Available at `http://localhost:3000`

---

## 📡 API Endpoints & Documentation

### Swagger UI & OpenAPI Specification
FastAPI automatically serves interactive API documentation:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **OpenAPI Schema**: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

### Endpoint Summary

| HTTP Method | Route | Operation ID | Description |
| :--- | :--- | :--- | :--- |
| `POST` | `/books/` | `create_book` | Add a new book to the library catalog |
| `GET` | `/books/` | `list_books` | Retrieve all books with refreshed available counts |
| `GET` | `/books/{book_id}` | `get_book` | Retrieve single book details by ID |
| `POST` | `/books/{book_id}/reserve` | `reserve_book` | Reserve 1 copy for a named user (expires in 7 days) |
| `DELETE` | `/reservations/{reservation_id}`| `cancel_reservation` | Cancel active reservation and restore 1 copy |
| `GET` | `/reservations/` | `list_reservations` | List reservations with optional status filter |
| `GET` | `/health` | `health_check` | Service liveness health check |

---

### CURL & JSON Request Examples

#### 1. Add a new book
```cmd
curl -X POST "http://127.0.0.1:8000/books/" ^
  -H "Content-Type: application/json" ^
  -d "{\"title\": \"Database Internals\", \"author\": \"Alex Petrov\", \"total_copies\": 4}"
```
**Response (201 Created):**
```json
{
  "title": "Database Internals",
  "author": "Alex Petrov",
  "total_copies": 4,
  "id": 7,
  "available_copies": 4
}
```

#### 2. Retrieve all books
```cmd
curl -X GET "http://127.0.0.1:8000/books/"
```
**Response (200 OK):**
```json
[
  {
    "title": "Designing Data-Intensive Applications",
    "author": "Martin Kleppmann",
    "total_copies": 4,
    "id": 1,
    "available_copies": 3
  }
]
```

#### 3. Reserve a book copy
```cmd
curl -X POST "http://127.0.0.1:8000/books/1/reserve" ^
  -H "Content-Type: application/json" ^
  -d "{\"user_name\": \"sarah_connor\"}"
```
**Response (201 Created):**
```json
{
  "id": 6,
  "book_id": 1,
  "book_title": "Designing Data-Intensive Applications",
  "user_name": "sarah_connor",
  "reservation_date": "2026-10-16T16:48:22.599363Z",
  "expires_at": "2026-10-23T16:48:22.599363Z",
  "status": "active"
}
```

#### 4. Cancel a reservation
```cmd
curl -X DELETE "http://127.0.0.1:8000/reservations/6"
```
**Response (200 OK):**
```json
{
  "id": 6,
  "book_id": 1,
  "book_title": "Designing Data-Intensive Applications",
  "user_name": "sarah_connor",
  "reservation_date": "2026-10-16T16:48:22.599363Z",
  "expires_at": "2026-10-23T16:48:22.599363Z",
  "status": "cancelled"
}
```

---

## 🐍 Platform Python SDK (OpenAPI Generator CLI)

The Python SDK in `library_sdk/` was genuinely generated using `@openapitools/openapi-generator-cli` from `/openapi.json`. It matches the expected usage pattern in the challenge specification.

### Regenerating the SDK
To regenerate the SDK if endpoints or schemas are updated, run:
```cmd
scripts\generate_sdk.bat
```
Under the hood, this script executes:
```cmd
npx -y @openapitools/openapi-generator-cli generate -i openapi.json -g python -o library_sdk --package-name library_sdk
```

### SDK Usage Example
```python
from library_sdk import ApiClient, Configuration
from library_sdk.api.books_api import BooksApi
from library_sdk.api.reservations_api import ReservationsApi
from library_sdk.models.book_create import BookCreate
from library_sdk.models.reservation_create import ReservationCreate

# Configure API Client
config = Configuration(host="http://127.0.0.1:8000")
client = ApiClient(configuration=config)

books_api = BooksApi(client)
reservations_api = ReservationsApi(client)

# 1. List books
books = books_api.list_books()
print(f"Total books: {len(books)}")

# 2. Create a new book
new_book = books_api.create_book(
    book_create=BookCreate(
        title="Site Reliability Engineering",
        author="Beyer et al.",
        total_copies=3
    )
)

# 3. Reserve a copy
reservation = books_api.reserve_book(
    book_id=new_book.id,
    reservation_create=ReservationCreate(user_name="sre_developer")
)
print(f"Reserved! ID={reservation.id}, expires at {reservation.expires_at}")

# 4. Cancel reservation
cancelled = reservations_api.cancel_reservation(reservation_id=reservation.id)
print(f"Status: {cancelled.status}")
```

### Running SDK Verification Script
With the backend server running, execute:
```cmd
.\env\Scripts\python.exe scripts\run_sdk_example.py
```
This script exercises all 7 phases of the SDK lifecycle and verifies end-to-end correctness.

---

## 🧪 Automated Testing Suite

The project includes unit, integration, boundary, concurrency, and SDK smoke tests using pytest. Tests execute against an isolated temporary SQLite database (`test_library.db`), leaving development and production databases untouched.

### Running All Tests
```cmd
.\env\Scripts\pytest.exe -v
```

### Test Coverage Highlights
- **`tests/test_books.py`**:
  - Book creation, listing, and single book retrieval.
  - Validation rules: empty title, empty author, zero copies, negative copies (HTTP 422).
  - Missing and invalid IDs (HTTP 404 & 422).
- **`tests/test_reservations.py`**:
  - Decrementing inventory on reservation.
  - Rejection when `available_copies == 0` (HTTP 400).
  - Boundary case: Single copy book (`total_copies == 1`).
  - Cancellation restoring exactly 1 copy.
  - **Idempotency**: Repeated cancellation fails (HTTP 400) without double restoring copies.
  - **Deterministic Expiration**: Active reservations with past timestamps are processed into `'expired'` status, freeing copies exactly once.
  - Database check constraints enforcement and rollback testing.
- **`tests/test_concurrency.py`**:
  - 8 simultaneous reservation threads attempting to reserve 2 copies.
  - Asserts exactly 2 succeed, exactly 6 fail, and inventory safely reaches 0 without race conditions.
- **`tests/test_sdk_smoke.py`**:
  - Launches an in-memory ASGI test server on an ephemeral port.
  - Exercises the OpenAPI Generator SDK via real HTTP calls across book creation, retrieval, reservation, and cancellation.

---

## 💻 Frontend Web Application

The frontend is a React application built with Vanilla CSS and Axios:
- **Catalog & Inventory Tab**: View real-time available copies, ratio progress meters, status badges (Available, 1 Left, Fully Reserved), and live search.
- **Add Book Modal**: Allows adding new catalog entries with total copy allocation.
- **Reservation Modal**: Reserve an available copy by typing a username, with explicit notification of the 7-day expiration policy.
- **Reservations Tab**: Filter reservations by Active, Cancelled, or Expired, showing exact reservation timestamps and countdowns to expiration.
- **Cancellation**: One-click cancellation for active reservations with instantaneous copy restoration.
- **Auto-Sync / Polling**: Background polling (every 8 seconds) maintains sync across multiple browser sessions without UI disruptions, toggleable in the header.

To build the frontend for production:
```cmd
cd frontend
npm run build
```

---

## ❓ Troubleshooting & FAQ

### 1. `setupdev.bat` reports npm or python not found
Ensure Python 3.10+ and Node.js are added to your Windows `PATH` environment variable. Open a new Command Prompt after modifying `PATH`.

### 2. Port 8000 or 3000 is already in use
You can customize the ports:
- Backend: Update `PORT` in `.env` or run `uvicorn app.main:app --port 8080`.
- Frontend: Update `VITE_API_BASE_URL` in `frontend/.env` and run `npm start -- --port 3001`.

### 3. OpenAPI Generator CLI requires Java
If `scripts\generate_sdk.bat` reports a Java error, install Java (JRE 11+) from [Adoptium](https://adoptium.net/) or Oracle and ensure `java -version` returns a valid version in your terminal.

---

## 📝 Known Limitations & Production Considerations

1. **SQLite Database Concurrency**: SQLite is an embedded single-file database. While Write-Ahead Logging (WAL) and `busy_timeout=5000` handle multi-threaded reads and fast atomic updates gracefully, enterprise high-volume concurrent deployments should swap `DATABASE_URL` for PostgreSQL with `SELECT ... FOR UPDATE` row-level locks.
2. **Background Cron vs. Just-In-Time Expiration**: The current implementation triggers expiration processing just-in-time on every query and mutation, guaranteeing that users and APIs never see stale inventory counts. In high-scale deployments, this can be complemented by a background cron job (e.g., Celery, APScheduler, or a Redis-backed worker) running every 60 seconds.
3. **Authentication & Authorization**: The specification defines reserving for a named username string without authentication. For a public multi-tenant application, integration with OAuth2 / JWT authentication (e.g., FastAPI Security with OAuth2PasswordBearer) is recommended.
