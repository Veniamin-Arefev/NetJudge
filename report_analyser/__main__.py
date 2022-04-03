import sys
from .appcmd import import_files, import_instructions, Repl


if __name__ == '__main__':
    '''Usage: python3 -m report_analyser REPORTS_DIR INSTRUCTIONS_DIR'''
    if (len(sys.argv) == 1):
        Repl().cmdloop()
    if (len(sys.argv) in [2, 3]):
        import_files([sys.argv[1],])
        if (len(sys.argv) > 2):
            import_instructions(sys.argv[2])
        Repl().do_start("3")