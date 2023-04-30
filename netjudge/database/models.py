"""All database models."""
from sqlalchemy import *
from sqlalchemy.orm import relationship
import datetime
import tarfile
import re
import hashlib

from netjudge.database.__init__ import *
from netjudge.email_helper.deadlines import deadlines as deadlines_dict
from netjudge.email_helper.mailer_configs import load_configs

_default_datetime = datetime.datetime.fromisoformat('2009-05-17 20:09:00')


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
        """Dict(json) data for student."""
        data = {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'grade': sum([task.grade for task in self.tasks]),
            'tasks': [task.json() for task in self.tasks],
        }
        return data


class Task(Base):
    """One task with all report files."""

    __tablename__ = 'task'

    student_id = Column(Integer, ForeignKey('student.id', ondelete='CASCADE'), nullable=False)
    student = relationship("Student", back_populates="tasks")
    reports = relationship("Report", back_populates="task")
    id = Column(Integer, primary_key=True)
    name = Column(String)
    creation_date = Column(DateTime, default=_default_datetime)
    grade = Column(Integer)
    is_plagiary = Column(Boolean, default=False)
    is_broken = Column(Boolean, default=False)
    regex_passed = Column(Integer, default=-1)
    regex_total = Column(Integer, default=-1)

    def __init__(self, student, name):
        """Initialise task object."""
        self.student = student
        self.name = name

    def json(self):
        """Dict (json) data from report."""
        data = {
            'id': self.id,
            'name': self.name,
            'creation_date': min([report.creation_date for report in self.reports]).strftime('%d-%m-%Y %H:%M:%S'),
            'grade': self.grade,
            'is_broken': self.is_broken,
            'is_plagiary': self.is_plagiary,
            'regex_passed': self.regex_passed,
            'regex_total': self.regex_total,
            'reports': [report.json() for report in self.reports],
        }
        return data


class Report(Base):
    """Report files and info."""

    __tablename__ = 'report'

    task_id = Column(Integer, ForeignKey('task.id', ondelete='CASCADE'), nullable=False)
    task = relationship("Task", back_populates="reports")
    id = Column(Integer, primary_key=True)
    name = Column(String)  # report.03.base
    text = Column(Text)
    creation_date = Column(DateTime, default=_default_datetime)
    hash = Column(String, default=hashlib.md5(str(datetime.datetime.now()).encode()).hexdigest())
    is_plagiary = Column(Boolean, default=False)
    is_broken = Column(Boolean, default=False)
    grade = Column(Integer)  # 0, 1, 2, 4
    regex_passed = Column(Integer, default=-1)
    regex_total = Column(Integer, default=-1)

    def __init__(self, task, file_path):
        """Initialise report object."""
        self.task = task
        self.name = os.path.basename(file_path)
        self.creation_date = _default_datetime
        try:
            file = tarfile.open(file_path)

            self.creation_date = self.get_report_date(file)
            self.hash = hashlib.md5(file.extractfile('./TIME.txt').read()).hexdigest()

            raw_text = file.extractfile('./OUT.txt').read()

            try:
                self.text = raw_text.decode()
            except Exception:
                try:
                    self.text = raw_text.decode('cp1251')
                except Exception:
                    self.text = raw_text.decode(errors="ignore")

        except Exception:
            self.text = ""
            self.is_broken = True

        self.set_grade()

    def json(self):
        """Dict (json) data from report."""
        data = {
            'id': self.id,
            'name': self.name,
            'is_plagiary': self.is_plagiary,
            'is_broken': self.is_broken,
            'creation_date': self.creation_date.strftime('%d-%m-%Y %H:%M:%S'),
            'grade': self.grade,
            'regex_passed': self.regex_passed,
            'regex_total': self.regex_total,
            'hash': self.hash,
            'text': self.text,
        }
        return data

    def get_report_date(self, file):
        """Report creation date."""
        line = file.extractfile('./TIME.txt').read().decode().split('\n')[0]
        time_lines = re.findall(r'START_TIME \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', line)
        if time_lines:
            creation_date = re.findall(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', time_lines[0])[0]
            return datetime.datetime.strptime(creation_date, '%Y-%m-%d %H:%M:%S')

    def set_grade(self):
        """Give report a grade."""
        configs = load_configs('mailer.cfg')

        cur_deadline = self.get_deadline()
        # get offset-naive datetime
        cur_deadline = datetime.datetime.strptime(cur_deadline.strftime('%d-%m-%Y %H:%M:%S'), '%d-%m-%Y %H:%M:%S')
        if self.is_plagiary:
            self.grade = int(configs['Rating grades']['plagiarism'])
        else:
            if self.creation_date < cur_deadline:
                self.grade = int(configs['Rating grades']['on_time'])
            elif self.creation_date < cur_deadline + datetime.timedelta(7):
                self.grade = int(configs['Rating grades']['week'])
            else:
                self.grade = int(configs['Rating grades']['fortnight'])
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
            return list(deadlines_dict.values())[index]
        else:
            raise ValueError("not enough parameters")
