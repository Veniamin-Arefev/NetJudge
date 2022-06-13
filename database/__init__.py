"""Database module initialisation."""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os


database_path = 'sqlite:///' + os.path.abspath('./data.db')
engine = create_engine(database_path)
_SessionFactory = sessionmaker(bind=engine)
Base = declarative_base()


def session_factory():
    """Creates session for database work."""
    Base.metadata.create_all(engine)
    return _SessionFactory()
