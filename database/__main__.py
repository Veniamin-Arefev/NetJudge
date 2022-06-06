from .functions import *
import json


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
    add_all_reports_in_tree(print_info=True)
    rate_reports()
    print(json.dumps(collect_data(), indent=4))
