"""FastAPI Application entrypoint and configuration."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.database import engine, Base
from app.routers import books, reservations


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: ensures tables exist on startup."""
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Library Book Reservation System API",
    description=(
        "Production-ready FastAPI service managing book inventories, "
        "concurrency-safe reservations with automatic 7-day expiration, "
        "and cancellation logic with inventory restoration."
    ),
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware for React frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(books.router)
app.include_router(reservations.router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom validation error handler providing clear error messages."""
    error_messages = []
    for err in exc.errors():
        loc = " -> ".join(str(l) for l in err.get("loc", []))
        msg = err.get("msg", "Validation error")
        error_messages.append(f"{loc}: {msg}")
    return JSONResponse(
        status_code=422,
        content={"detail": "; ".join(error_messages)},
    )


@app.get(
    "/health",
    tags=["System"],
    summary="Health check",
    operation_id="health_check",
)
def health_check():
    """Health check endpoint to verify backend service liveness."""
    return {
        "status": "healthy",
        "service": "Library Book Reservation System",
        "version": "1.0.0",
    }


@app.get(
    "/",
    tags=["System"],
    summary="Root service info",
    operation_id="root_info",
)
def root():
    """Root info redirecting users to docs."""
    return {
        "message": "Welcome to the Library Book Reservation System API",
        "docs_url": "/docs",
        "openapi_url": "/openapi.json",
    }
