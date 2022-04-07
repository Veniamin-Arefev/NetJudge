import sys
from .appcmd import import_files, import_instructions, Repl
import argparse

arg_parser = argparse.ArgumentParser(prog='NET-Judge',
                                     description='Check imported reports with imported instructions.')
                                     
arg_parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
arg_parser.add_argument('-q', '--quiet', action='store_true', help='show only final marks.') # Not implemented yet

arg_parser.add_argument('reports directory', metavar='REP_DIR', nargs='?', type=str, default='', 
                        help='Directory, contains reports in format REPORT.NUMBER.MACHINE')
arg_parser.add_argument('instructions directory', metavar='INS_DIR', nargs='?', type=str, default='', 
                        help='Directory, includes instructions: Single file for each task. Format: INSTR.NUMBER')

# TODO: quiet regime.
if __name__ == '__main__':
    '''Usage: python3 -m report_analyser REPORTS_DIR INSTRUCTIONS_DIR'''
    args = arg_parser.parse_args()
    if (len(sys.argv) == 1):
        Repl().cmdloop()
    if (len(sys.argv) in [2, 3]):
        import_files([sys.argv[1],])
        if (len(sys.argv) > 2):
            import_instructions(sys.argv[2])
        Repl().do_start("3")