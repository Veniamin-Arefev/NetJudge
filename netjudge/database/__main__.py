"""Database."""
import argparse

from netjudge.database.functions import *


def main():
    """Main function."""
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('action', type=str, default='parse', choices=['parse', 'export'])
    arg_parser.add_argument('--file_name', nargs='?', type=str, default='data', help='Export file name')
    arg_parser.add_argument('--tasks_dir', nargs='?', type=str, default='tasks')

    args = arg_parser.parse_args()

    if args.action == "parse":
        add_all_reports_in_tree(args.tasks_dir, print_info=True)
        rate_reports(print_info=True)
    elif args.action == "export":
        export_to_csv(args.first_argument)
        export_to_csv_regex("regex_" + args.first_argument)


if __name__ == "__main__":
    main()
