from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

#database_path = 'sqlite:///:memory:'
database_path = 'sqlite:///' + os.path.abspath('./data.db')
# sqlite:///relative/path/to/file.db
# sqlite:///:memory: - создать в оперативной памяти
engine = create_engine(database_path)
_SessionFactory = sessionmaker(bind=engine)

Base = declarative_base()


def session_factory():
    Base.metadata.create_all(engine)
    return _SessionFactory()
