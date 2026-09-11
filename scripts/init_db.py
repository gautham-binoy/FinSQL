import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.database.connection import init_database, settings


def main():
    print(f"Initializing database using: {settings.DATABASE_URL}")
    init_database()
    print("Database tables initialized successfully.")


if __name__ == "__main__":
    main()
