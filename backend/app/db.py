import os
from sqlalchemy import create_engine

PG_HOST = os.getenv("POSTGRES_HOST", "localhost")
PG_PORT = os.getenv("POSTGRES_PORT", "5432")
PG_DB   = os.getenv("POSTGRES_DB", "ans_db")
PG_USER = os.getenv("POSTGRES_USER", "postgres")
PG_PASS = os.getenv("POSTGRES_PASSWORD")

if not PG_PASS:
    raise RuntimeError("POSTGRES_PASSWORD não definido (env var).")

DATABASE_URL = f"postgresql://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)
