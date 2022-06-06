import os.path

import email_helper.mailer_utilities
from . import *
from .models import *
from report_analyser.translator import translate
from email_helper.deadlines import deadlines as deadlines_dict


def get_deadline(task_number=None, task_name=None):
    """Return deadline date for task
    :param task_number: Number of required task
    :param task_name: Name of required task
    :return: Deadline date as datetime.date object
    """

    if task_number is not None:
        return list(deadlines_dict.values())[task_number]
    elif task_name is not None:
        try:
            index = list(deadlines_dict.keys()).index(task_name)
        except ValueError:
            return None
        return list(deadlines_dict.values())[index]
    else:
        raise ValueError("not enough parameters")


def add_report(email, report_path):
    """Adds report to person"""

    session = session_factory()

    """Get or create person"""
    person = session.query(Person).filter(Person.email == email).first()
    if not person:
        try:
            mailer_utilities = email_helper.mailer_utilities.MailerUtilities(
                email_helper.mailer_utilities.get_ya_mailbox())
            username = mailer_utilities.get_username_by_email(email)
        except Exception:
            username = "Undefined"
            pass
        person = Person(username, email)
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
        if (same_reports := session.query(Report).filter(Report.hash == report.hash)).count() > 1:
            for clone in same_reports:
                clone.plagiat = True
                session.commit()

        """Rate report"""
        report.grade = report.get_grade()
        session.commit()
    else:
        """Check new report date"""
        new_report = Report(task, report_path)
        if new_report.create_date >= report.create_date:
            session.delete(report)
        else:
            session.delete(new_report)

        session.commit()
    task.grade = max([report.grade for report in task.reports])
    session.commit()
    session.close()


def add_all_reports_in_tree(reports_path):
    pass


def get_lines(email, report_name):
    """Find report input and output"""

    session = session_factory()
    person = session.query(Person).filter(Person.email == email).first()
    if not person:
        return None

    task_number = int(report_name[7:9])
    task = session.query(Task).filter(Task.number == task_number).filter(Task.person_id == person.id).first()
    if not task:
        return None

    report = session.query(Report).join(Task).filter(Task.person == person).filter(Report.name == report_name).first()
    if not report:
        return None
    text = re.sub('\r', '', report.text)
    lines = [translate(line) for line in text.split('\n') if line]
    session.close()
    return lines


def get_student_grades(email):
    """Find student's grades for each completed task"""

    session = session_factory()
    person = session.query(Person).filter(Person.email == email).first()
    if not person:
        return None

    tasks = session.query(Task).filter(Task.person_id == person.id)
    if not tasks:
        return None

    return {
        'summary': sum([task.grade for task in tasks]),
        'tasks': [{'task': task.number, 'grade': task.grade, 'report_count': len(task.reports)} for task in tasks]
    }


def get_all_grades():
    """Find grades for every student"""

    session = session_factory()
    students = session.query(Person)
    session.close()
    return [{'email': student.email, 'data': get_student_grades(student.email)} for student in students]

