from nexusflow.db.session import engine, Session, get_db
from nexusflow.db.models import Base

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
