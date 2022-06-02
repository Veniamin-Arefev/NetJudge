from .models import *
from . import *


def add_task_to_person(person, number):
    """Create new task object for this person."""

    print("Number = ", number)
    new_task = Task(person.id, number)
    session.add(new_task)
    session.commit()
    print(new_task.person_id)
    
    
def add_report_to_person(person, file_path):
    """Find or create task and add new report to it."""

    report_name = os.path.basename(file_path)
    task_number = int(report_name[7:9])  # позиции строго фиксированы
    if task_number not in [task.number for task in person.tasks]:
        person.add_task(task_number)
    task = session.query(Task).filter(Task.number == task_number).filter(Task.person_id == person.id)[0]
    if report_name in [report.name for report in task.reports]:
        return  # это задание уже добавлено
    add_report_to_task(task, file_path)
    print("TN", task.number)
    session.commit()


def add_report_to_task(task, file_path):
    """Add report file for this task object."""

    new_report = Report(task.id, file_path)
    session.add(new_report)
    session.commit()


def check_report_originality(report):
    """Find reports with the same hash"""

    if session.query(Report).filter(Report.hash == report.hash)[0]:
        report.plagiat = True
    else:
        report.plagiat = False
    report.save()

def get_report_date(file):
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

def set_report_grade(report, deadline):
    if report.plagiat:
        report.grade = 0
    else:
        report.grade = 1
    report.save()