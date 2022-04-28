from .models import Person
from . import *


def create_test():
    session = session_factory()
    shrek = Person("Shrek", "shrek@dreamworks.com")
    session.add(shrek)
    session.commit()
    session.close()


def get_people():
    session = session_factory()
    people_query = session.query(Person)
    session.close()
    return people_query.all()


if __name__ == "__main__":
    people = get_people()
    if len(people) == 0:
        print("No one found")
        create_test()
    people = get_people()
    for person in people:
        print(person)
