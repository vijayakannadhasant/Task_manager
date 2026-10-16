"""Pydantic schemas for request validation and response serialization."""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Title of the book")
    author: str = Field(..., min_length=1, max_length=255, description="Author of the book")
    total_copies: int = Field(..., gt=0, description="Total number of copies (must be greater than 0)")

    @field_validator("title", "author")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Field must not be empty or whitespace only")
        return stripped


class BookCreate(BookBase):
    pass


class BookResponse(BookBase):
    id: int = Field(..., description="Unique ID of the book")
    available_copies: int = Field(..., ge=0, description="Number of currently available copies")

    model_config = ConfigDict(from_attributes=True)


class ReservationCreate(BaseModel):
    user_name: str = Field(..., min_length=1, max_length=100, description="Username of the person reserving the book")

    @field_validator("user_name")
    @classmethod
    def strip_username(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("Username must not be empty or whitespace only")
        return stripped


class ReservationResponse(BaseModel):
    id: int = Field(..., description="Unique ID of the reservation")
    book_id: int = Field(..., description="ID of the reserved book")
    book_title: Optional[str] = Field(None, description="Title of the reserved book")
    user_name: str = Field(..., description="Username of the reserver")
    reservation_date: datetime = Field(..., description="UTC timestamp when reservation was created")
    expires_at: datetime = Field(..., description="UTC timestamp when reservation expires")
    status: str = Field(..., description="Status of reservation: 'active', 'cancelled', or 'expired'")

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    message: str = Field(..., description="Informational message")
    reservation: Optional[ReservationResponse] = Field(None, description="Updated reservation object")


class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Detailed description of the error")
