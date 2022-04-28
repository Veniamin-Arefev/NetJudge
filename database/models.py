from sqlalchemy import Column, String, Date, Integer
from sqlalchemy.orm import sessionmaker

from . import *


class Person(Base):
    """Class for one person."""

    __tablename__ = 'persons'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)

    def __init__(self, name, email):
        self.name = name
        self.email = email

    def __repr__(self):
        return f"Name: {self.name}\nemail: {self.email}"
