from sqlalchemy import *
from sqlalchemy.orm import relationship
import datetime
import tarfile
import re
import os
import hashlib

from . import *
from .translator import translate  # потом переделать


class Person(Base):
    """Class for one person."""

    __tablename__ = 'person'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    tasks = relationship("Task", back_populates="person")

    def __init__(self, name, email):
        """Initialise person object

        :param name: Person's name
        :param email: Person's email
        """

        self.name = name
        self.email = email

    def __repr__(self):
        """Person str"""

        line = f"Name: {self.name}\nemail: {self.email}\n"
        line += f"Completed tasks: "
        for task in self.tasks:
            line += str(task.number) + ','
        return line


class Task(Base):
    """One task with all report files"""

    __tablename__ = 'task'

    person_id = Column(Integer, ForeignKey('person.id', ondelete='CASCADE'), nullable=False)
    person = relationship("Person", back_populates="tasks")
    reports = relationship("Report", back_populates="task")
    id = Column(Integer, primary_key=True)
    number = Column(Integer)
    deadline = Column(Date)

    def __init__(self, person, number, deadline):
        """Initialise task object."""

        self.person = person
        self.number = number
        self.deadline = deadline


class Report(Base):
    """Report files and info"""

    __tablename__ = 'report'

    task_id = Column(Integer, ForeignKey('task.id', ondelete='CASCADE'), nullable=True)
    task = relationship("Task", back_populates="reports")
    id = Column(Integer, primary_key=True)
    name = Column(String)  # report.03.base
    text = Column(Text)
    input = Column(Text)
    output = Column(Text)
    create_date = Column(Date)
    hash = Column(String)
    grade = Column(Float)  # 0, 0.25, 0.5. 1

    def __init__(self, task, file_path):
        """Initialise report object"""

        self.task = task
        self.plagiat = False
        self.name = os.path.basename(file_path)
        file = tarfile.open(file_path)
        self.text = file.extractfile('./OUT.txt').read().decode()
        text = re.sub('\r', '', self.text)  # re.split работал не совсем так, как надо
        lines = [translate(line) for line in text.split('\n') if line]
        self.input = '\n'.join([line[1] for line in lines if line[0] == 'input'])
        self.output = '\n'.join([line[1] for line in lines if line[0] == 'output'])
        self.create_date = self.get_report_date(file)
        self.get_report_date(file)
        self.hash = hashlib.md5(file.extractfile('./TIME.txt').read()).hexdigest()

    def __repr__(self):
        """Report str"""

        line = f"Name: {self.name}\n"
        line += f"Creation date: {self.create_date.strftime('%d.%m.%y')}\n"
        line += f"Hash: {self.hash}\n"
        line += f"Grade: {self.grade}"
        return line

    def get_report_date(self, file):
        """Report creation date"""

        line = file.extractfile('./TIME.txt').read().decode().split('\n')[0]
        time_lines = re.findall(r'START_TIME \d{4}-\d{2}-\d{2}', line)
        if time_lines:
            create_date = re.findall(r'\d{4}-\d{2}-\d{2}', time_lines[0])[0]
            year, month, day = create_date.split('-')
            date = datetime.date(day=int(day), month=int(month), year=int(year))
            return date
        else:  # едва ли это нужно
            raise ValueError()

    def get_grade(self, deadline):
        """Give report a grade"""

        if self.plagiat:
            grade = 0
        else:
            if (deadline - self.create_date).days < 7:
                grade = 1
            elif (deadline - self.create_date).days < 14:
                grade = 0.5
            else:
                grade = 0.25

        return grade
