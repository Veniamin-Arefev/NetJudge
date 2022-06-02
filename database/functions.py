import os.path
from . import *
from .models import *

def get_deadline(task_number=None, task_name=None):
    """Return deadline date for task
    :param task_number: Number of required task
    :param task_name: Name of required task
    :return: Deadline date as datetime.date object
    """

    return datetime.date.today()


def add_report(email, report_path):
    """Adds report to person"""

    session = session_factory()

    """Get or create person"""
    person = session.query(Person).filter(Person.email == email).first()
    if not person:
        person = Person("Name", email)
        session.add(person)
        session.commit()

    """Get or create task"""
    report_name = os.path.basename(report_path)
    task_number = int(report_name[7:9])  # позиции строго фиксированы
    deadline = get_deadline(task_number)
    task = session.query(Task).filter(Task.number == task_number).filter(Task.person_id == person.id).first()
    if not task:
        task = Task(person, task_number, deadline)
        session.add(task)
        session.commit()

    """Add report if it isn't already added"""
    report = session.query(Report).join(Task).filter(Task.person == person).filter(Report.name == report_name).first()
    if not report:
        report = Report(task, report_path)
        session.add(report)
        session.commit()

        """Check plagiat"""
        if session.query(Report).filter(Report.hash == report.hash).count() > 1:
            report.plagiat = True
            session.commit()

        """Rate report"""
        report.grade = report.get_grade(deadline)
        session.commit()

    print("Grade ", report.grade)
    session.close()
