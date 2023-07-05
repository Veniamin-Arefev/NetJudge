import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

__all__ = ['engine', 'Session']

database_path = 'sqlite:///' + os.path.abspath('./data.db')
engine = create_engine(database_path)
Session = sessionmaker(engine)
