"""Database."""
import argparse

from ..database.functions import *


def main():
    """Main function."""
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('action', type=str, default='parse', choices=['parse', 'export'])
    arg_parser.add_argument('first_argument', nargs='?', type=str, default='',
                            help='export_file_name or report_username')
    arg_parser.add_argument('report_name', nargs='?', type=str, default='')

    args = arg_parser.parse_args()

    if args.action == "parse":
        add_all_reports_in_tree(print_info=True)
        rate_reports()
    elif args.action == "export":
        export_to_csv(args.first_argument)
        export_to_csv_regex("regex_" + args.first_argument)


if __name__ == "__main__":
    main()
