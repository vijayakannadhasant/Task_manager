"""SQLAlchemy database models for books and reservations."""
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    CheckConstraint,
    text,
    TypeDecorator,
)
from sqlalchemy.orm import relationship
from app.database import Base


class UTCDateTime(TypeDecorator):
    """Ensure datetimes are stored and loaded as timezone-aware UTC datetimes."""
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            if value.tzinfo is not None:
                return value.astimezone(timezone.utc)
            return value.replace(tzinfo=timezone.utc)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            if value.tzinfo is None:
                return value.replace(tzinfo=timezone.utc)
            return value.astimezone(timezone.utc)
        return value


def utc_now():
    """Return current UTC datetime with timezone awareness."""
    return datetime.now(timezone.utc)


class Book(Base):
    """Book model representing library inventory."""
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    total_copies = Column(Integer, nullable=False)
    available_copies = Column(Integer, nullable=False)

    reservations = relationship(
        "Reservation",
        back_populates="book",
        cascade="all, delete-orphan",
        order_by="Reservation.reservation_date.desc()",
    )

    __table_args__ = (
        CheckConstraint("total_copies > 0", name="check_total_copies_positive"),
        CheckConstraint("available_copies >= 0", name="check_available_copies_non_negative"),
        CheckConstraint("available_copies <= total_copies", name="check_available_copies_le_total"),
    )


class Reservation(Base):
    """Reservation model representing a reserved book copy by a user."""
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id", ondelete="CASCADE"), nullable=False, index=True)
    user_name = Column(String(100), nullable=False)
    reservation_date = Column(
        UTCDateTime,
        nullable=False,
        default=utc_now,
        server_default=text("CURRENT_TIMESTAMP"),
    )
    expires_at = Column(UTCDateTime, nullable=False)
    status = Column(
        String(20),
        nullable=False,
        default="active",
        server_default="active",
        index=True,
    )

    book = relationship("Book", back_populates="reservations")

    __table_args__ = (
        CheckConstraint("status IN ('active', 'cancelled', 'expired')", name="check_reservation_status"),
    )
