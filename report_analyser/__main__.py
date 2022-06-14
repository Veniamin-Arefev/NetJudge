"""Report analyser."""
import sys
from .appcmd import GL_Mode, import_files_from_dir, import_instructions_from_json, Repl, print_red, _, \
    import_files_from_base
import argparse

arg_parser = argparse.ArgumentParser(prog='NET-Judge',
                                     description='Check imported reports with imported instructions.')

arg_parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.1')
arg_parser.add_argument('-q', '--quiet', action='store_true', help='show only final marks.')  # Not implemented yet

arg_parser.add_argument('reports_source_type', metavar='SOURCE_TYPE', nargs='?', type=str, default='',
                        choices=['DIR', 'DATABASE', 'CMD', ''],
                        help='Choose, whether reports are imported from local \
                        directory or server database or use interactive cmd mode.')
arg_parser.add_argument('reports_directory', metavar='REP_DIR', nargs='?', type=str, default='',
                        help='Directory, contains directories with reports in format REPORT.NUMBER.MACHINE')
arg_parser.add_argument('instructions_file', metavar='INS_DIR', nargs='?', type=str, default='',
                        help='Instruction file, that contains regexes')

def main():
    """Main cmd function."""
    args = arg_parser.parse_args()
    if args.quiet:
        global GL_Mode
        GL_Mode = "quiet"
    if args.reports_source_type in ["CMD", ""]:
        Repl().cmdloop()
    elif args.reports_source_type in ["DIR", "DATABASE"]:
        if args.reports_source_type == "DIR":
            if args.reports_directory == '':
                print_red(_("Not enough arguments, see '--help'"))
                sys.exit()
            else:
                import_files_from_dir([args.reports_directory, ])
                if args.instructions_file != '':
                    import_instructions_from_json([args.instructions_file, ])
        elif args.reports_source_type == "DATABASE":
            import_files_from_base()
            Repl().cmdloop()
            # Решил сделать, чтобы регулярки можно было вставлять только с локальной системы,
            # поэтому дальше переходим в режим проверки через cli
            pass
        Repl().do_start("2")
        Repl().do_conclude("")

if __name__ == '__main__':
    main()
