import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER") or os.getenv("POSTGRES_USER", "mi_usuario")
DB_PASSWORD = os.getenv("DB_PASSWORD") or os.getenv(
    "POSTGRES_PASSWORD", "mi_password_seguro"
)
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT") or os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("DB_NAME") or os.getenv("POSTGRES_DB", "mi_base_datos")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
)
