from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings

# Prefer explicit DATABASE_URL when provided, otherwise construct from parts
if settings.DATABASE_URL:
    DATABASE_URL = settings.DATABASE_URL
else:
    db_name = settings.MYSQL_DB or settings.MYSQL_DATABASE
    DATABASE_URL = (
        f"mysql+pymysql://{settings.MYSQL_USER}:"
        f"{settings.MYSQL_PASSWORD}@{settings.MYSQL_HOST}:"
        f"{settings.MYSQL_PORT}/{db_name}"
    )

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
