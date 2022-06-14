"""Database."""
import argparse
from sys import platform

from .functions import *


def main():
    """Main function."""
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('action', type=str, default='parse', choices=['parse', 'export', 'getinfo', 'printinfo'])
    arg_parser.add_argument('first_argument', nargs='?', type=str, default='',
                            help='export_file_name or report_username')
    arg_parser.add_argument('report_name', nargs='?', type=str, default='')

    args = arg_parser.parse_args()

    if args.action == "parse":
        add_all_reports_in_tree(print_info=True)
        rate_reports()
    elif args.action == "export":
        export_to_csv(args.first_argument)
    elif args.action == "getinfo":
        output = []
        if platform.startswith('win'):
            true_username = args.first_argument.encode('cp866').decode('utf-8')
        else:
            true_username = args.first_argument
        for file_name in homeworks_names_and_files[args.report_name]:
            output.append(f"""            
                        <tr> 
                            <th>{file_name}</th>
                            <th><pre>{get_report_text(name=true_username, report_name=file_name)}
                            </pre></th>
                        </tr>""")

        print(''.join(output))


if __name__ == "__main__":
    main()
