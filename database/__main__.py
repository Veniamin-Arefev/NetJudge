from .models import *
from . import *
import datetime


def create_test():
    session = session_factory()

    shrek = Person("Shrek", "shrek@dreamworks.com")
    session.add(shrek)
    session.commit()

    shrek.add_report('/home/dmitry/Documents/netjudge_tests/report4/report.04.base')
    session.commit()

    session.close()


def get_people():
    session = session_factory()
    people_query = session.query(Person)
    session.close()
    return people_query.first()


def print_statistics():
    session = session_factory()
    people_query = session.query(Person)
    for person in people_query:
        print(person)
        print('-' * 10)
        for task in person.tasks:
            print(task)
            for report in task.reports:
                print(report)
    session.close()


if __name__ == "__main__":
    session = session_factory()
    shrek = Person("Shrek", "shrek@dreamworks.com")
    session.add(shrek)
    session.commit()

    shrek.add_report('/home/dmitry/Documents/netjudge_tests/report4/report.04.base', datetime.datetime.today() - datetime.timedelta(days=8))
    session.commit()
    session.close()
    print_statistics()
