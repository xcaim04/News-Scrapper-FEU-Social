import os
import time
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    db_user = os.getenv("DB_USER") or os.getenv("POSTGRES_USER", "mi_usuario")
    db_password = os.getenv("DB_PASSWORD") or os.getenv(
        "POSTGRES_PASSWORD", "mi_password_seguro"
    )
    db_host = os.getenv("DB_HOST", "db")
    db_port = os.getenv("DB_PORT") or os.getenv("POSTGRES_PORT", "5432")
    db_name = os.getenv("DB_NAME") or os.getenv("POSTGRES_DB", "mi_base_datos")

    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


DATABASE_URL = get_database_url()
engine = create_engine(DATABASE_URL, future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

# Ensure all models are imported so Base.metadata includes them before create_all()
import app.schemas.models  # noqa: F401


def connect_db(timeout: int = 60, interval: int = 5) -> None:
    deadline = time.time() + timeout

    while True:
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            print("Database connection successful.")
            break
        except OperationalError as error:
            if time.time() >= deadline:
                print("Timed out waiting for database.")
                raise
            print(
                f"Database connection failed: {error}. Retrying in {interval} seconds..."
            )
            time.sleep(interval)

    Base.metadata.create_all(bind=engine)
    print("Database tables created or already exist.")


if __name__ == "__main__":
    connect_db()
