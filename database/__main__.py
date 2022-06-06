import datetime
import json
from .models import *
from . import *
from .functions import *


def get_people():
    session = session_factory()
    people_query = session.query(Student)
    session.close()
    return people_query.first()


def print_statistics():
    session = session_factory()
    people_query = session.query(Student)
    for student in people_query:
        print(student)
        print('-' * 10)
        for task in student.tasks:
            print(task)
            for report in task.reports:
                print(report)
            print()
    session.close()


if __name__ == "__main__":
    add_report("shrek@dreamworks.com", '/home/dmitry/Documents/netjudge_tests/report5/report_05.router')
    #add_report("shrek@dreamworks.com", 'tasks' + os.sep + '01_HardwareAndCommandline' + os.sep + 'veniamin.arefev@mail.ru'
               #+ os.sep + '1' + os.sep + 'report.01.clone')
    #print_statistics()
    #print(get_student_data("shrek@dreamworks.com"))
    print(json.dumps(get_all_grades(), indent=4))
    print(get_lines("report_05_client1.client1", email="shrek@dreamworks.com"))
