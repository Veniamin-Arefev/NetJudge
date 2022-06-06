import sys
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
    if len(sys.argv) > 3:
        if sys.argv[-3] == 'getinfo':
            output = []
            for file_name in homeworks_names_and_files[sys.argv[-1]]:
                output.append(f"""            
                <tr> 
                    <th>{file_name}</th>
                    <th>{get_report_text(name=sys.argv[-2], report_name=file_name)}</th>
                </tr>""")
    else:
        add_all_reports_in_tree(print_info=True)
        rate_reports()
    # print(collect_data())
