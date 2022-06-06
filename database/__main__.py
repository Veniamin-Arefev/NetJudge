import datetime
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
    for person in people_query:
        print(person)
        print('-' * 10)
        for task in person.tasks:
            print(task)
            for report in task.reports:
                print(report)
    session.close()


if __name__ == "__main__":
    # add_report("shrek@dreamworks.com", '/home/dmitry/Documents/netjudge_tests/report4/report.04.base')
    # add_report("shrek@dreamworks.com", 'tasks' + os.sep + '01_HardwareAndCommandline' + os.sep + 'veniamin.arefev@mail.ru'
    #            + os.sep + '1' + os.sep + 'report.01.clone')
    add_all_reports_in_tree(print_info=True)
    # print_statistics()
