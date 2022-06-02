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
    tasks = relationship("Task")

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

    def add_task(self, number, deadline=None):
        """Create new task object for this person."""

        print("Number = ", number)
        session = session_factory()
        new_task = Task(self.id, number, deadline)
        session.add(new_task)
        session.commit()
        print(new_task.person_id)
        session.close()

    def add_report(self, file_path, deadline=None):
        """Find or create task and add new report to it."""

        report_name = os.path.basename(file_path)
        task_number = int(report_name[7:9])  # позиции строго фиксированы
        session = session_factory()
        if task_number not in [task.number for task in self.tasks]:
            self.add_task(task_number, deadline)
        task = session.query(Task).filter(Task.number == task_number).filter(Task.person_id == self.id)[0]
        if report_name in [report.name for report in task.reports]:
            return  # это задание уже добавлено
        task.add_report(file_path)
        print("TN", task.number)
        session.commit()
        session.close()


class Task(Base):
    """One task with all report files"""

    __tablename__ = 'task'

    person_id = Column(Integer, ForeignKey('person.id', ondelete='CASCADE'), nullable=False)
    id = Column(Integer, primary_key=True)
    number = Column(Integer)
    reports = relationship("Report")
    deadline = Column(Date)

    def __init__(self, person_id, number, deadline):
        """Initialise task object."""

        self.person_id = person_id
        self.number = number
        self.deadline = deadline

    def add_report(self, file_path):
        """Add report file for this task object."""

        session = session_factory()
        new_report = Report(self.id, file_path)
        session.add(new_report)
        new_report.set_grade(self.deadline)
        session.commit()
        session.close()


class Report(Base):
    """Report files and info"""

    __tablename__ = 'report'

    task_id = Column(Integer, ForeignKey('task.id', ondelete='CASCADE'), nullable=True)
    id = Column(Integer, primary_key=True)
    name = Column(String)  # report.03.base
    text = Column(Text)
    input = Column(Text)
    output = Column(Text)
    create_date = Column(Date)
    hash = Column(String)
    grade = Column(Float)  # 0, 0.25, 0.5. 1

    def __init__(self, task_id, file_path):
        """Initialise report object"""
        self.task_id = task_id
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

    def check_originality(self):
        """Find reports with the same hash"""

        session = session_factory()
        if session.query(Report).filter(Report.hash == self.hash).count() > 1:
            self.plagiat = True
        session.commit()
        session.close()

    def __repr__(self):
        """Report str"""

        session = session_factory()
        line = f"Name: {self.name}\n"
        session.close()
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

    def set_grade(self, deadline):
        """Give report a grade"""

        session = session_factory()
        self.check_originality()
        if self.plagiat:
            self.grade = 0
        else:
            if (deadline - self.create_date).days < 7:
                self.grade = 1
            elif (deadline - self.create_date).days < 14:
                self.grade = 0.5
            else:
                self.grade = 0.25
        session.commit()
        session.close()
