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
    """Adds report to student"""

    session = session_factory()

    """Get or create student"""
    student = session.query(Student).filter(Student.email == email).first()
    if not student:
        try:
            mailer_utilities = email_helper.mailer_utilities.MailerUtilities(
                email_helper.mailer_utilities.get_ya_mailbox())
            username = mailer_utilities.get_username_by_email(email)
        except Exception:
            username = "Undefined"
            pass
        student = Student(username, email)
        session.add(student)
        session.commit()

    """Get or create task"""
    report_name = os.path.basename(report_path)
    task_number = int(report_name[7:9])  # позиции строго фиксированы
    deadline = get_deadline(task_number)
    task = session.query(Task).filter(Task.number == task_number).filter(Task.student_id == student.id).first()
    if not task:
        task = Task(student, task_number, deadline)
        session.add(task)
        session.commit()

    """Add report if it isn't already added"""
    report = session.query(Report).join(Task).filter(Task.student == student).filter(Report.name == report_name).first()
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
        if new_report.create_date > report.create_date:
            """Adding new report"""

            session.delete(report)
            session.commit()
            session.add(new_report)
            session.commit()
        else:
            """New report is older"""

            session.delete(task.reports[-1])
            session.commit()

    task.grade = max([report.grade for report in task.reports])
    session.commit()
    session.close()


def add_all_reports_in_tree(reports_path='tasks', print_info=False):
    for homework_name in os.listdir(reports_path):
        if print_info:
            print(f"Current importing task : {homework_name}", end="\r")
        for email in os.listdir(reports_path + os.sep + homework_name):
            for report_try in os.listdir(reports_path + os.sep + homework_name + os.sep + email):
                for filename in os.listdir(reports_path + os.sep
                                           + homework_name + os.sep + email + os.sep + report_try):
                    """Check the correctness of the file"""
                    try:
                        add_report(email,
                                   reports_path + os.sep +
                                   homework_name + os.sep +
                                   email + os.sep +
                                   report_try + os.sep +
                                   filename)
                    except Exception:
                        pass


def get_lines(report_name, email=None, name=None):
    """Find report input and output"""

    session = session_factory()

    """Find student"""
    if email:
        student = session.query(Student).filter(Student.email == email).first()
        if not student:
            return None
    elif name:
        student = session.query(Student).filter(Student.name == name).first()
        if not student:
            return None
    else:
        return None

    """Find task"""
    task_number = int(report_name[7:9])
    task = session.query(Task).filter(Task.number == task_number).filter(Task.student_id == student.id).first()
    if not task:
        return None

    """Find report"""
    report = session.query(Report).join(Task).filter(Task.student == student).filter(Report.name == report_name).first()
    if not report:
        return None
    text = re.sub('\r', '', report.text)
    lines = [translate(line) for line in text.split('\n') if line]
    session.close()
    return lines


def get_student_data(email):
    """Find student's grades for each completed task"""

    session = session_factory()

    """Find student"""
    student = session.query(Student).filter(Student.email == email).first()
    if not student:
        return None

    data = student.json()
    session.close()
    return data


def get_all_grades():
    """Find grades for every student"""

    session = session_factory()
    students = session.query(Student)
    data = [student.json() for student in students]
    session.close()
    return data
