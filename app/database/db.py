from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from app.config import Config

Base = declarative_base()

engine = create_engine(Config.DATABASE_URI)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

def init_db():
    # Import all modules that define models
    from app.models.document import Document
    Base.metadata.create_all(bind=engine)

def get_db():
    try:
        yield db_session
    finally:
        db_session.remove()
