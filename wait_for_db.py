import argparse
import os
import sys
import time
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

load_dotenv()


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        print(f"Using DATABASE_URL from environment: {database_url}")
        return database_url

    db_user = os.getenv("DB_USER") or os.getenv("POSTGRES_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD") or os.getenv("POSTGRES_PASSWORD", "postgres")
    db_host = os.getenv("DB_HOST", "db")
    db_port = os.getenv("DB_PORT") or os.getenv("POSTGRES_PORT", "5432")
    db_name = os.getenv("DB_NAME") or os.getenv("POSTGRES_DB", "news_scrapper")
    print(
        f"Constructing DB URL for user='{db_user}', db='{db_name}', host='{db_host}', port='{db_port}'"
    )
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


def wait_for_db(url: str, timeout: int = 60, interval: int = 5) -> bool:
    engine = create_engine(url, future=True)
    deadline = time.time() + timeout

    while time.time() < deadline:
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            print("Database is ready.")
            return True
        except OperationalError as error:
            print(f"Waiting for database... ({error})", flush=True)
            time.sleep(interval)

    print(f"Timeout reached while waiting for the database ({timeout}s).", flush=True)
    return False


def parse_args():
    parser = argparse.ArgumentParser(description="Wait for PostgreSQL to be ready.")
    parser.add_argument("--timeout", type=int, default=60, help="Seconds to wait")
    parser.add_argument("--interval", type=int, default=5, help="Retry interval in seconds")
    parser.add_argument("--url", default=None, help="Optional DATABASE_URL override")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to run after db is ready")
    return parser.parse_args()


def main():
    args = parse_args()
    database_url = args.url or get_database_url()

    if not wait_for_db(database_url, timeout=args.timeout, interval=args.interval):
        sys.exit(1)

    command = args.command or ["python", "main.py"]
    print(f"Starting command: {' '.join(command)}")
    os.execvp(command[0], command)


if __name__ == "__main__":
    main()
