"""
appcmd.py
=====================================
Console
"""

import tarfile
import sys
import os
import re
import shlex
import cmd
import gettext
from report_analyser.input_checker.Machine_config import Machine
from .translator import translate
from collections import defaultdict
from termcolor import colored, cprint

'''Project l10n & i18n'''
translation = gettext.translation('netjudge', 'po', fallback=True)
_, ngettext = translation.gettext, translation.ngettext

'''Cmd colors'''

'''  For regex'''
print_magenta = lambda x: cprint(x, 'magenta')
'''  For standart system output'''
print_cyan = lambda x: cprint(x, 'cyan')
'''  For positive user experience'''
print_green = lambda x: cprint(x, 'green')
'''  For negative user experience'''
print_red = lambda x: cprint(x, 'red')
'''  For undefined user experience'''
print_yellow = lambda x: cprint(x, 'yellow')
'''  Standart prompt'''
print_blue = lambda x: cprint(x, 'blue')
'''  Regex prompt'''
print_magenta = lambda x: cprint(x, 'magenta')

''' Global structures

GL_Instr holds imported instruction files:
  key = instruction name (name of file)
  value = instruction data'''
GL_Instr = dict()
''' GL_Files, GL_Result_#:
  key = participant name (if imported from dir -
                          name of dir with reports)
  value = python3 dictionary:
    key = report name
    value = participant data on this report'''
GL_Files = defaultdict(dict)
GL_Result_1 = dict()
GL_Result_2 = dict()
GL_Result_3 = dict()
''' GL_Regex holds regexes used for checking'''
GL_Regex = []

def import_files_from_dir(dir_paths):
    '''Add keys to GF_Files'''
    for dir_path in dir_paths:
        '''Find all dirs = users'''
        for user_dir in [dir[0] for dir in os.walk(dir_path)]:
            try:
                file_names = [filename for filename in os.listdir(user_dir) if
                            re.fullmatch(r"report.\d+.[^\.:]*", filename)] 
            except FileNotFoundError as E:
                print(E)
                continue
            for filename in file_names:
                checkname = filename.split(".")
                if checkname[0] != "report":
                    print_red(f"ERROR: Wrong file format \'{filename}\'. It should start with \'report\'!")
                    continue
                try:
                    checknumber = int(checkname[1])
                except Exception as E:
                    print_red(f"ERROR: Wrong file format \'{filename}\'. Report number should be integer!")
                    continue
                print(colored(user_dir, attrs=['bold']), " ", filename)
                GL_Files[user_dir][filename] = ""
        

def import_instructions_from_dir(dir_paths):
    '''Add keys to GF_Instr'''
    for dir_path in dir_paths:
        try:
            file_names = [filename for filename in os.listdir(dir_path) if
                          re.fullmatch(r"instruction.\d+.[^\.:]*", filename)] 
        except Exception as E:
            print(E)
            continue
        for filename in file_names:
            checkname = ".".join(filename.split(".")[1:])
            for usercont in GL_Files.values():
                for filewithpath in usercont.keys():
                    if checkname == filewithpath[-len(checkname):]:
                        print(colored(dir_path, attrs=['bold']), " ", filename)
                        GL_Instr[dir_path + '/' + filename] = ""

def Syntax_check():
    """Parse files & Write score in GL_Result_1"""
    machines = {}
    for user_dir, userfiles in GL_Files.items():
        print("Participant: '", user_dir, "', his files:\n\t", end="")
        for userfile in userfiles.keys():
            # TODO: FORDIMA: Modernize this fun
            filename = user_dir + "/" + userfile
            print(filename)
            number = filename.split(".")[-2]
            machine_name = filename.split("/")[-1]
            obj = tarfile.open(filename)
            obj_members = obj.getmembers()
            text = obj.extractfile('./OUT.txt').read().decode()
            text = re.sub('\r', '', text)  # re.split работал не совсем так, как надо
            lines = [translate(line) for line in text.split('\n') if line]
            GL_Files[user_dir][userfile] = lines
            machines[machine_name + number] = Machine(machine_name, number, lines)
        print(f'Task number: {int(number)}')
        for machine in machines.values():
            machine.print_log()
        # TODO: FORDIMA: Fill GL_Result_1 with score of syntax check. Keys are filenames, same as GL_Files.keys()
        # GL_Result_1 = ...

def Inner_semantic_check():
    """Write score in GL_Result_2"""
    pass 
    # TODO: Inner_semantic_check():

def Outer_semantic_check():
    """Write score in GL_Result_3"""
    pass 
    # TODO: Outer_semantic_check():

def print_exit_message():
    print_cyan(_("\n ==[ Exiting! ]=="))

def print_help():
    pass 
    # TODO: Add help for all the cmd variety

def print_help_regex():
    pass 
    # TODO: Add help for all the cmd variety

class Repl_Regex(cmd.Cmd):
    prompt = colored(_("[ NetJu REGEX ]:~$ "), 'magenta')
    mode = "brief"

    def do_help(self, arg):
        print_help_regex()
        self.lastcmd = ''

    def do_addre(self, arg):
        """Check REPORTs with REGEX"""
        self.lastcmd = ''

    def do_mode(self, arg):
        """Modify verbosity mode"""
        args = shlex.split(arg, comments=True)
        if len(args) != 1:
            print_red(_("Wrong number of arguments"))
        else:
            if args[0] not in ["quiet", "brief", "verbose"]:
                print_red(_('Wrong argument. Use one of "quiet", "brief", "verbose"'))
            else:
                self.mode = args[0]
                print_green(_("'{}' mode is set.").format(args[0]))
        self.lastcmd = ''

    def complete_mode(self, text, allcommand, beg, end):
        return [s for s in ["quiet", "brief", "verbose",] if s.startswith(text)]

    def do_q(self, arg):
        """Easier exit"""
        return True

    def do_exit(self, arg):
        return True
    # TODO: Make cmd history recover after exiting regex mode

class Repl(cmd.Cmd):
    prompt = colored(_("[ NetJu ]:~$ "), 'blue')
    print_cyan(_(" ==[ Welcome to NET-JUDGE - Check enviroment for iproute2 library! ]==\n"))

    def do_nothing(self, arg):
        """Present to ease change between cmds"""
        pass

    def do_help(self, arg):
        print_help()

    def do_q(self, arg):
        """Easier exit"""
        print_exit_message()
        return True

    def do_exit(self, arg):
        print_exit_message()
        return True

    def do_reset(self, arg):
        """This function clears all results achieved and imports made."""
        global GL_Files, GL_Instr, GL_Result_1, GL_Result_2, GL_Result_3
        GL_Files = GL_Instr = GL_Result_1 = GL_Result_2 = GL_Result_3 = dict()
        print_cyan(_(" ==[ All progress is reset!! ]==\n"))

    def do_importedreports(self, arg):
        """Print imported report files"""
        if not GL_Files:
            print_cyan(_("  =[ No reports imported ]="))
        else:
            print_cyan(_("  =[ Imported reports: ]="))
            for username, userfiles in GL_Files.items():
                print("Participant: ", colored(username, attrs=['bold']), " His files:\n\t", end="")
                for userfile in userfiles.keys():
                    print(userfile, end="\t ")
                print("")

    def do_importedinstructions(self, arg):
        """Print imported instruction files"""
        if not GL_Instr:
            print_cyan(_("  =[ No instructions imported ]="))
        else:
            print_cyan(_("  =[ Imported instructions: ]="))
            for filename in GL_Instr.keys():
                print(filename, end="\t")
            print("")

    def do_addrep(self, arg):
        """AddRep is used to add files to the collection.
        
        Input: Target directories to extract files from.
        Output: List of imported files.
        """
        args = shlex.split(arg, comments=True)
        if len(args) == 0:
            print_red(_("Not enough arguments"))
        else:
            dir_paths = args[0:]
            import_files_from_dir(dir_paths)            

    def do_addins(self, arg):
        """AddIns is used to add instruction files to the collection.
        Instr. files contain info on how objects depend from each other.
        This information is important for the last step of checking.

        Input: Target directories to extract instructions from.
        Output: List of imported instruction files.
        """
        args = shlex.split(arg, comments=True)
        if len(args) == 0:
            print_red(_("Not enough arguments"))
        else:
            dir_paths = args[0:]
            import_instructions_from_dir(dir_paths)   

    def do_start(self, arg):
        """Main function to start checking process. Checking steps:

        1. Parsing & Syntax check;
        2. Inner semantic check;
        3. Outer semantic check.

        No files in collection:              # # # steps done
        Files present in collection:         1 2 # steps done
        Instructions present in collection:  1 2 3 steps done

        Input: Number of steps done.
        Output: Result.
        """
        args = shlex.split(arg, comments=True)
        if len(args) not in [0, 1]:
            print_red(_("Wrong number of arguments"))
        else: 
            if len(args) == 1:
                if args[0] not in ["1", "2", "3", "regex", "re"]:
                    print_yellow(_("Wrong number of steps to be done: {}").format(args[0]))
                    steps = 0
                elif args[0] not in ["regex", "re"]:
                    steps = int(arg[0])
                else:
                    steps = 1
            else:
                steps = 3
            if not GL_Files.keys():
                steps = min(steps, 0)
                print_yellow(_('''No report files imported! => No steps would be done!\nUse \'addf REPORT_FILES_DIR\''''))
            if not GL_Instr.keys() and (len(args) == 0 or len(args) == 1 and args[0] not in ["regex", "re"]):
                steps = min(steps, 2)
                print_yellow(_('''No instruction files imported! => Third step is skipped\nUse \'addins INSTRUCTION_FILE\''''))

            if len(args) == 1 and args[0] in ["regex", "re"]:
                '''Check with regexs'''
                print_cyan(_("  ==[ CHECK WITH REGEXs STARTS: ]=="))
                Repl_Regex().cmdloop()
                '''Otherwise last cmd is called after return'''
                self.lastcmd = 'nothing'
            else:
                '''Check with imported instructions'''
                print_cyan(_("  ==[ CHECK STARTS:  Going through {} steps ]==").format(steps))
                if steps > 0: 
                    print_cyan(_("  =[ SYNTAX CHECK ]="))
                    Syntax_check() 
                if steps > 1: 
                    print_cyan(_("  =[ INNET SEMANTIC CHECK ]="))
                    Inner_semantic_check() 
                if steps > 2: 
                    print_cyan(_(" =[ OUTER SEMANTIC CHECK ]="))
                    Outer_semantic_check()
            print_cyan(_("  ==[ CHECK ENDED ]=="))   

    def complete_start(self, text, allcommand, beg, end):
        return [s for s in ["1", "2", "3", "regex", "re",] if s.startswith(text)]

    def conclude(self, arg):
        """Function prints general result for each task number presented
        in collection
        """
        # TODO: Make marks
