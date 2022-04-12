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

'''Project l10n & i18n'''
translation = gettext.translation('netjudge', 'po', fallback=True)
_, ngettext = translation.gettext, translation.ngettext

'''Structures to hold imported files and instructions.
Each dict has a name of file as a key.
'''
GL_Files = dict()
GL_Instr = dict()
GL_Result_1 = dict()
GL_Result_2 = dict()
GL_Result_3 = dict()

def import_files(dir_paths):
    '''Add keys to GF_Files'''
    for dir_path in dir_paths:
        try:
            file_names = [filename for filename in os.listdir(dir_path) if
                          re.fullmatch(r"report.\d+.[^\.:]*", filename)] 
        except FileNotFoundError as E:
            print(E)
            continue
        for filename in file_names:
            checkname = filename.split(".")
            if checkname[0] != "report":
                print(f"ERROR: Wrong file format \'{filename}\'. It should start with \'report\'!")
                continue
            try:
                checknumber = int(checkname[1])
            except Exception as E:
                print(f"ERROR: Wrong file format \'{filename}\'. Report number should be integer!")
                continue
            GL_Files[dir_path + '/' + filename] = ""
        

def import_instructions(dir_paths):
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
            print(checkname)
            for filewithpath in GL_Files.keys():
                if checkname == filewithpath[-len(checkname):]:
                    GL_Instr[dir_path + '/' + filename] = ""

def Syntax_check():
    """Parse files & Write score in GL_Result_1"""
    machines = {}
    for filename in GL_Files.keys():
        # TODO: FORDIMA: Modernize this fun
        print(filename)
        number = filename.split(".")[-2]
        machine_name = filename.split("/")[-1]
        obj = tarfile.open(filename)
        obj_members = obj.getmembers()
        text = obj.extractfile('./OUT.txt').read().decode()
        text = re.sub('\r', '', text)  # re.split работал не совсем так, как надо
        lines = [translate(line) for line in text.split('\n') if line]
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
    print(_("\n ==[ Exiting! ]=="))

def print_help():
    pass 
    # TODO: Add help for all the cmd variety

class Repl(cmd.Cmd):
    prompt = _("[ NetJu ]:~$ ")
    print(_(" ==[ Welcome to NET-JUDGE - Check enviroment for iproute2 library! ]==\n"))

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
        print(_(" ==[ All progress is reset!! ]==\n"))

    def do_importedreports(self, arg):
        """Print imported report files"""
        if not GL_Files:
            print(_("  =[ No reports imported ]="))
        else:
            print(_("  =[ Imported reports: ]="))
            for filename in GL_Files.keys():
                print(filename, end="\t")
            print("")

    def do_importedinstructions(self, arg):
        """Print imported instruction files"""
        if not GL_Instr:
            print(_("  =[ No instructions imported ]="))
        else:
            print(_("  =[ Imported instructions: ]="))
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
            print(_("Not enough arguments"))
        else:
            dir_paths = args[0:]
            import_files(dir_paths)            

    def do_addins(self, arg):
        """AddIns is used to add instruction files to the collection.
        Instr. files contain info on how objects depend from each other.
        This information is important for the last step of checking.

        Input: Target directories to extract instructions from.
        Output: List of imported instruction files.
        """
        args = shlex.split(arg, comments=True)
        if len(args) == 0:
            print(_("Not enough arguments"))
        else:
            dir_paths = args[0:]
            import_instructions(dir_paths)   

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
        if len(args) != 1:
            steps = 3
        else: 
            if args[0] not in ["1", "2", "3",]:
                print(_("Wrong number of steps to be done: {}").format(args[0]))
                steps = 0
            else:
                steps = int(arg[0])
        if not GL_Files.keys():
            steps = min(steps, 0)
            print(_('''No report files imported! => No steps would be done!
    Use \'addf REPORT_FILES_DIR\''''))
        if not GL_Instr.keys():
            steps = min(steps, 2)
            print(_('''No instruction files imported! => Third step is skipped
    Use \'addins INSTRUCTION_FILE\''''))

        print(_("  ==[ CHECK STARTS:  Going through {} steps ]==").format(steps))
        if steps > 0: 
            print(_("  =[ SYNTAX CHECK ]="))
            Syntax_check() 
        if steps > 1: 
            print(_("  =[ INNET SEMANTIC CHECK ]="))
            Inner_semantic_check() 
        if steps > 2: 
            print(_(" =[ OUTER SEMANTIC CHECK ]="))
            Outer_semantic_check()
        print(_("  ==[ CHECK ENDED ]=="))   

    def complete_start(self, text, allcommand, beg, end):
        return [s for s in ["1", "2", "3",] if s.startswith(text)]

    def conclude(self, arg):
        """Function prints general result for each task number presented
        in collection
        """
        # TODO: Make marks
