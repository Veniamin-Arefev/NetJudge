from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import relationship
import datetime
import tarfile
import re

from . import *
from .translator import translate  # потом переделать


class Person(Base):
    """Class for one person."""

    __tablename__ = 'person'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    reports = relationship("Report")

    def __init__(self, name, email):
        self.name = name
        self.email = email

    def __repr__(self):
        return f"Name: {self.name}\nemail: {self.email}"

    def add_report(self, file_path):
        session = session_factory()
        new_report = Report(self.id, file_path)
        session.add(new_report)
        session.commit()
        session.close()


class Report(Base):
    """Report files and info"""

    __tablename__ = 'report'

    person_id = Column(Integer, ForeignKey('person.id', ondelete='CASCADE'), nullable=False)
    id = Column(Integer, primary_key=True)
    text = Column(Text)
    input = Column(Text)
    output = Column(Text)
    create_time = Column(DateTime)
    hash = Column(String)

    def __init__(self, person_id, file_path):
        self.person_id = person_id
        file = tarfile.open(file_path)
        self.text = file.extractfile('./OUT.txt').read().decode()
        text = re.sub('\r', '', self.text)  # re.split работал не совсем так, как надо
        lines = [translate(line) for line in text.split('\n') if line]
        self.input = '\n'.join([line for line in lines if line[1] == 'input'])
        self.output = '\n'.join([line for line in lines if line[1] == 'output'])
        time_file = file.extractfile('./TIME.txt').read().decode()
        print(time_file)
        self.create_time = datetime.datetime.now()
        self.hash = 'HASH'

