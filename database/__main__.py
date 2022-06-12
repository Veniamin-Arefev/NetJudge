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


def main():
    if len(sys.argv) > 3:
        if sys.argv[-3] == 'getinfo':
            output = []
            true_username = sys.argv[-2].encode('cp866').decode('utf-8')
            for file_name in homeworks_names_and_files[sys.argv[-1]]:
                output.append(f"""            
                            <tr> 
                                <th>{file_name}</th>
                                <th><pre>{get_report_text(name=true_username, report_name=file_name)}
                                </pre></th>
                            </tr>""")

            print(''.join(output))
    else:
        add_all_reports_in_tree(print_info=True)
        rate_reports()


if __name__ == "__main__":
    main()
