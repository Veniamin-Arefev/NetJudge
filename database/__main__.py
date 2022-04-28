from .models import *
from . import *


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


if __name__ == "__main__":
    person = get_people()
    session = session_factory()
    person.add_report('/home/dmitry/Documents/netjudge_tests/report4/report.04.base')
    session.commit()
    print(person.tasks[1].reports)
    print(len(person.tasks))
