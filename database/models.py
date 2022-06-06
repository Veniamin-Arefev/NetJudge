from sqlalchemy import *
from sqlalchemy.orm import relationship
import datetime
import tarfile
import re
import hashlib

from . import *
from email_helper.deadlines import deadlines as deadlines_dict



class Student(Base):
    """Class for one student."""

    __tablename__ = 'student'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    tasks = relationship("Task", back_populates="student")

    def __init__(self, name, email):
        """Initialise student object

        :param name: Student's name
        :param email: Student's email
        """

        self.name = name
        self.email = email

    def json(self):
        """Dict(json) data for student"""

        data = {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'grade': sum([task.grade for task in self.tasks]),
            'tasks': [task.json() for task in self.tasks],
        }
        return data

    def __repr__(self):
        """Student str"""

        line = f"Name: {self.name}\nemail: {self.email}\n"
        line += f"Completed tasks: "
        for task in self.tasks:
            line += str(task.number) + ','
        return line


class Task(Base):
    """One task with all report files"""

    __tablename__ = 'task'

    student_id = Column(Integer, ForeignKey('student.id', ondelete='CASCADE'), nullable=False)
    student = relationship("Student", back_populates="tasks")
    reports = relationship("Report", back_populates="task")
    id = Column(Integer, primary_key=True)
    name = Column(String)
    creation_date = Column(Date, default=datetime.date.today())
    grade = Column(Integer, default=0)
    is_plagiat = Column(Boolean, default=False)

    def __init__(self, student, name):
        """Initialise task object."""

        self.student = student
        self.name = name

    def json(self):
        """Dict (json) data from report"""

        data = {
            'id': self.id,
            'number': self.number,
            'create_date': min([report.create_date for report in self.reports]).strftime('%d.%m.%Y'),
            'grade': self.grade,
            'reports': [report.json() for report in self.reports],
        }
        return data

    def __repr__(self):
        return str(self.number) + ' ' + str(self.grade)


class Report(Base):
    """Report files and info"""

    __tablename__ = 'report'

    task_id = Column(Integer, ForeignKey('task.id', ondelete='CASCADE'), nullable=True)
    task = relationship("Task", back_populates="reports")
    id = Column(Integer, primary_key=True)
    name = Column(String)  # report.03.base
    text = Column(Text)
    create_date = Column(Date)
    hash = Column(String)
    is_plagiat = Column(Boolean, default=False)
    grade = Column(Integer)  # 0, 1, 2, 4

    def __init__(self, task, file_path):
        """Initialise report object"""

        self.task = task
        self.name = os.path.basename(file_path)
        file = tarfile.open(file_path)
        self.text = file.extractfile('./OUT.txt').read().decode()
        self.create_date = self.get_report_date(file)
        self.hash = hashlib.md5(file.extractfile('./TIME.txt').read()).hexdigest()
        self.get_grade()

    def __repr__(self):
        """Report str"""

        line = f"Name: {self.name}\n"
        line += f"Creation date: {self.create_date.strftime('%d.%m.%y')}\n"
        line += f"Hash: {self.hash}\n"
        line += f"Grade: {self.grade}"
        return line

    def json(self):
        """Dict (json) data from report"""

        data = {
            'id': self.id,
            'name': self.name,
            'create_date': self.create_date.strftime('%d.%m.%Y'),
            'grade': self.grade,
            'hash': self.hash,
        }
        return data

    def get_report_date(self, file):
        """Report creation date"""

        line = file.extractfile('./TIME.txt').read().decode().split('\n')[0]
        time_lines = re.findall(r'START_TIME \d{4}-\d{2}-\d{2}', line)
        if time_lines:
            create_date = re.findall(r'\d{4}-\d{2}-\d{2}', time_lines[0])[0]
            year, month, day = create_date.split('-')
            date = datetime.date(day=int(day), month=int(month), year=int(year))
            return date

    def get_grade(self):
        """Give report a grade"""

        cur_deadline = self.get_deadline()
        if self.is_plagiat:
            self.grade = 0
        else:
            if self.create_date < cur_deadline:
                self.grade = 4
            elif self.create_date < cur_deadline + datetime.timedelta(7):
                self.grade = 2
            else:
                self.grade = 1
        return self.grade

    def get_deadline(self):
        """Return deadline date for task

        :param task_name: Name of required task
        :return: Deadline date as datetime.date object
        """

        task_name = self.task.name
        if task_name is not None:
            try:
                index = list(deadlines_dict.keys()).index(task_name)
            except ValueError:
                return None
            return list(deadlines_dict.values())[index].date()
        else:
            raise ValueError("not enough parameters")
