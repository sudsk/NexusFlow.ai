from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
import os

# Get database connection parameters from environment variables
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "nexusflow")
DB_USER = os.environ.get("DB_USER", "nexusflow-user")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")

# Create connection string
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Check connection before using
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,  # Recycle connections after 1 hour
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a scoped session
Session = scoped_session(SessionLocal)

# Dependency for FastAPI
def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()
