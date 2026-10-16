"""Entrypoint script for running the FastAPI application."""
import uvicorn
from app.config import settings

if __name__ == "__main__":
    print(f"Starting Library Book Reservation System on http://{settings.HOST}:{settings.PORT}")
    print(f"Swagger UI documentation available at: http://{settings.HOST}:{settings.PORT}/docs")
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False,
    )
