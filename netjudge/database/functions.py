"""Misc database functions."""
import os.path
import csv
from netjudge.database.models import *
from netjudge.report_analyser.translator import translate
from netjudge.email_helper.deadlines import homeworks_names_and_files
from netjudge.email_helper.mailer_utilities import MailerUtilities, get_ya_mailbox


def get_task_name(report_name):
    """Find task name by one of it's reports"""
    task_number = report_name[7:9]  # позиции строго фиксированы
    task_names = homeworks_names_and_files.keys()
    tasks = [task_name for task_name in task_names if task_name.startswith(task_number)]
    return tasks[0] if tasks else None


def add_all_reports_in_tree(reports_path='tasks', print_info=False):
    """Store all reports as file tree."""
    for homework_name in os.listdir(reports_path):
        if print_info:
            print(f"Current importing task : {homework_name}", end="\r")
        for email in os.listdir(reports_path + os.sep + homework_name):
            for report_try in os.listdir(reports_path + os.sep + homework_name + os.sep + email):
                for filename in os.listdir(reports_path + os.sep + homework_name + os.sep +
                                           email + os.sep + report_try):
                    """Check the correctness of the file"""
                    add_report(email,
                               reports_path + os.sep +
                               homework_name + os.sep +
                               email + os.sep +
                               report_try + os.sep +
                               filename)


def add_report(email, report_path):
    """Adds report to student"""
    session = session_factory()

    """Get or create student"""
    student = session.query(Student).filter(Student.email == email).first()
    if not student:
        try:
            mailer_utilities = MailerUtilities(get_ya_mailbox())
            username = mailer_utilities.get_username_by_email(email)
        except Exception:
            username = "Undefined"
            pass
        student = Student(username, email)
        session.add(student)
        session.commit()

    """Get or create task"""
    report_name = os.path.basename(report_path)
    task_name = get_task_name(report_name)
    task = session.query(Task).filter(Task.name == task_name).filter(Task.student_id == student.id).first()
    if not task:
        task = Task(student, task_name)
        session.add(task)
        session.commit()

    """Add report if it isn't already added"""
    report = session.query(Report).join(Task).filter(Task.student == student).filter(Report.name == report_name).first()
    if not report:

        """Add completely new report"""
        report = Report(task, report_path)
        session.add(report)
        session.commit()
    else:

        """Check new report date"""
        new_report = Report(task, report_path)
        if new_report.creation_date > report.creation_date:

            """Replacing older report by new one"""
            session.delete(report)
            session.commit()
            session.add(new_report)
            session.commit()
        else:

            """New report is older"""
            session.delete(task.reports[-1])
            session.commit()

    task.creation_date = min([report.creation_date for report in task.reports])
    if sum([1 for report in task.reports if report.is_broken]):
        task.is_broken = True
    else:
        task.is_broken = False
    session.commit()
    session.close()


def rate_reports(print_info=False):
    """Gives grade to every report and check plagiary"""
    session = session_factory()
    tasks = session.query(Task)
    if print_info:
        print("Rating reports")
    for task in tasks:

        """Task is confirmed plagiary"""
        if task.is_plagiary:
            task.grade = 0
            for report in task.reports:
                report.is_plagiary = True
                report.grade = 0
            session.commit()
        else:
            """Check originality"""
            for report in task.reports:
                if (same_reports := session.query(Report).filter(Report.hash == report.hash)).count() > 1:
                    """Found new plagiary"""
                    for clone in same_reports:
                        clone.task.is_plagiary = True
                        clone.task.grade = 0
                        for report in clone.task.reports:
                            report.is_plagiary = True
                            report.grade = 0
                    session.commit()
                else:
                    """Report seems to pe original"""
                    report.set_grade()
                    session.commit()
            if not task.is_plagiary:
                task.grade = min([report.grade for report in task.reports]) if task.reports else 0
                session.commit()

        """Task is broken if it has not all of required reports"""
        report_names = [report.name for report in task.reports]
        if sorted(report_names) != sorted(homeworks_names_and_files[task.name]):
            task.is_broken = True
            session.commit()

        if task.is_broken:
            task.grade = 0
            session.commit()

    session.close()
    if print_info:
        print("Finished")


def get_report_text(report_name, email=None, name=None):
    """Find report input and output"""
    session = session_factory()

    """Find student"""
    if email:
        student = session.query(Student).filter(Student.email == email).first()
        if not student:
            return ''
    elif name:
        student = session.query(Student).filter(Student.name == name).first()
        if not student:
            return ''
    else:
        return ''

    """Find report"""
    report = session.query(Report).join(Task).filter(Task.student == student).filter(Report.name == report_name).first()
    if not report or report.is_broken:
        return ''
    text = re.sub('\r', '', report.text)
    lines = [translate(line) for line in text.split('\n') if line]
    text = ''
    for line in lines:
        # if len(line[1].strip()) > 0:
        text += ("in | " if line[0] == 'input' else "out| ") + line[1] + '\n'
    session.close()
    return text


def get_student_data(email):
    """Find student's grades for each completed task."""
    session = session_factory()

    """Find student."""
    student = session.query(Student).filter(Student.email == email).first()
    if not student:
        return None

    data = student.json()
    session.close()
    return data


def collect_data():
    """Find grades for every student."""
    session = session_factory()
    students = session.query(Student)
    data = [student.json() for student in students]
    session.close()
    return data


def export_to_csv(filename):
    """Find grades for every student."""
    with open(filename, 'w', encoding='utf-8', newline='') as outfile:
        out_csv = csv.writer(outfile)
        session = session_factory()

        out_csv.writerow(['Username', 'Email', *homeworks_names_and_files.keys(), 'Total grade'])

        mails = [item[0] for item in session.query(Student.email)]

        for cur_email in mails:
            elems = []
            elems.append(session.query(Student.name).filter(Student.email == cur_email).first()[0])
            name, domain = cur_email.split('@')
            elems.append(f'{name[:3]}*@{domain}')

            submitted_tasks = {key: value for key, *value in
                               session.query(Task.name, Task.creation_date, Task.grade, Task.is_plagiary,
                                             Task.is_broken).join(Student).filter(Student.email == cur_email)}

            for homework_name in homeworks_names_and_files.keys():
                if homework_name in submitted_tasks.keys():
                    if submitted_tasks[homework_name][1] == 4:
                        elems.append('on time')
                    elif submitted_tasks[homework_name][1] == 2:
                        elems.append('week')
                    elif submitted_tasks[homework_name][1] == 1:
                        elems.append('fortnight')
                    elif submitted_tasks[homework_name][2] == 1 \
                            and submitted_tasks[homework_name][3] == 0:  # not original and not broken
                        elems.append('plagiarism')
                    else:
                        elems.append('broken')
                else:
                    elems.append('nope')
            elems.append(str(sum([item[1] for item in submitted_tasks.values()])))

            out_csv.writerow(elems)

        session.close()


def export_to_csv_regex(filename):
    """Find grades for every student."""
    with open(filename, 'w', encoding='utf-8', newline='') as outfile:
        out_csv = csv.writer(outfile)
        session = session_factory()

        out_csv.writerow(['Username', 'Email', *homeworks_names_and_files.keys()])

        mails = [item[0] for item in session.query(Student.email)]

        for cur_email in mails:
            elems = []
            elems.append(session.query(Student.name).filter(Student.email == cur_email).first()[0])
            name, domain = cur_email.split('@')
            elems.append(f'{name[:3]}*@{domain}')

            submitted_tasks = {key: value for key, *value in
                               session.query(Task.name, Task.creation_date, Task.grade, Task.is_plagiary,
                                             Task.is_broken, Task.regex_passed, Task.regex_total
                                             ).join(Student).filter(Student.email == cur_email)}

            for homework_name in homeworks_names_and_files.keys():
                if homework_name in submitted_tasks.keys():
                    regex_passed = int(submitted_tasks[homework_name][4])
                    regex_total = int(submitted_tasks[homework_name][5])
                    if regex_total != 0 and regex_total != -1:
                        elems.append(f"{regex_passed / regex_total:.4f}")
                    else:
                        elems.append("0")
                else:
                    elems.append('0')
            out_csv.writerow(elems)

        session.close()
