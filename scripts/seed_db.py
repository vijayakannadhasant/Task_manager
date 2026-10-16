"""Script to seed the SQLite database using seed_data.sql."""
import sqlite3
import os
import sys

# Add parent directory to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from app.config import settings

def seed_database():
    db_file = settings.DATABASE_URL.replace("sqlite:///", "")
    seed_sql_path = os.path.join(BASE_DIR, "seed_data.sql")

    if not os.path.exists(seed_sql_path):
        print(f"Error: seed_data.sql not found at {seed_sql_path}")
        sys.exit(1)

    print(f"Applying seed data to {db_file}...")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    with open(seed_sql_path, "r", encoding="utf-8") as f:
        sql_content = f.read()

    try:
        # Clear existing seed data if any
        cursor.execute("DELETE FROM reservations;")
        cursor.execute("DELETE FROM books;")
        cursor.executescript(sql_content)
        conn.commit()
        print("Database successfully seeded with realistic sample books and reservations!")
    except Exception as e:
        conn.rollback()
        print(f"Failed to seed database: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    seed_database()
