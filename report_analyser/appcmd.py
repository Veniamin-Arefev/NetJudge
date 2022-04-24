"""
appcmd.py
=====================================
Console
"""

import argparse
import tarfile
import sys
import os
import re
import shlex
import cmd
import gettext
import json
from report_analyser.input_checker.Machine_config import Machine
from .translator import translate
from collections import defaultdict
from termcolor import colored, cprint

'''Project l10n & i18n'''
translation = gettext.translation('netjudge', 'po', fallback=True)
_, ngettext = translation.gettext, translation.ngettext

'''Cmd colors'''
print_cyan = lambda x: cprint(x, 'cyan')
'''  For standart system output'''
print_green = lambda x: cprint(x, 'green')
'''  For positive user experience'''
print_red = lambda x: cprint(x, 'red')
'''  For negative user experience'''
print_yellow = lambda x: cprint(x, 'yellow')
'''  For undefined user experience'''
print_blue = lambda x: cprint(x, 'blue')
'''  Standart prompt'''
print_magenta = lambda x: cprint(x, 'magenta')
'''  Regex prompt'''

''' Global structures'''
GL_Files = defaultdict(dict)
''' GL_Files:
  key = participant name (if imported from dir -
                          name of dir with reports)
  value = python3 dictionary:
    key = report name
    value = participant data on this report'''
GL_Result_1 = defaultdict(dict)
GL_Result_2 = defaultdict(dict)
''' GL_Files, GL_Result_#:
  key = participant name (if imported from dir -
                          name of dir with reports)
  value = python3 dictionary:
    key = report name
    value = list:
      list[0] = current grade
      list[1] = maximum grade'''
GL_Regex = []
''' GL_Regex holds regexes used for checking
  GL_Regex[0] = regular expression
  GL_Regex[1] = files, it is applied to'''
GL_Mode = "brief"

def import_files_from_dir(dir_paths):
    '''Add keys to GF_Files'''
    once = True
    for dir_path in dir_paths:
        '''Find all dirs = users'''
        for user_dir in [dir[0] for dir in os.walk(dir_path)]:
            try:
                file_names = [filename for filename in os.listdir(user_dir) if
                              re.fullmatch(r"report.\d+.[^\.:]*", filename)] 
            except FileNotFoundError as E:
                print_red(E)
                continue
            else:
                if once:
                    print_green(_('Success'))
                    once = False
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
                GL_Result_2[user_dir][filename] = [0, 0]
        

def import_instructions_from_json(json_paths):
    '''Add keys to GF_Instr'''
    once = True
    global GL_Regex
    for filename in json_paths:
        try:
            with open(filename, 'r') as f:
                datastore = json.load(f)
                try:
                    for record in datastore:
                        record['regex']
                        record['inout']
                        record['files']
                        assert record['inout'] in ['in', 'out']
                except Exception as E:
                    print_red(_('Instruction json file contains invalid structures!'))
                    print_red(_("It must be list: [{'regex': STRING, 'inout': in/out 'files': [STRING, STRING]}, ..."))
                else:
                    GL_Regex += datastore
                    if once:
                        print_green(_('Success'))
                        once = False
                    for record in datastore:
                        print_regex_record(record)
        except FileNotFoundError as E:
            print_red(E)
            continue

def Syntax_correct():
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

def Semantic_check():
    """Write score in GL_Result_2"""
    #print(GL_Regex, GL_Files)
    global GL_Result_2
    for username, reportdict in GL_Files.items():
        print_blue(colored(_("Checking participant '{}':").format(username), attrs=['bold']))
        for reportname, lines in reportdict.items():
            print_blue(_("\n  Checking file {}:").format(reportname))
            regexlist = [regex for regex in GL_Regex if reportname in regex['files'] or regex['files'] == ['']]
            for regexind, regex in enumerate(regexlist):
                print_cyan(_("    RE {}: '{}' ({}put).").format(regexind, regex['regex'], regex['inout']))
                find = False
                matchind = 0
                #print(lines)
                for lineind, line in enumerate(lines):
                    #print(line)
                    if line[0].startswith(regex['inout']):
                        patt = re.compile(regex['regex'])
                        for match in patt.findall(line[1]):
                            find = True
                            matchind += 1
                            print("      "+colored(_("Match {} in line {}:").format(matchind, lineind), attrs=["bold"]))
                            linewithmatch = colored(match, "green", attrs=["underline"]).join(line[1].split(match))
                            print(_("        {}").format(colored(linewithmatch)))
                if not find:
                    print_red(_("      No matches in {} lines!").format(lineind+1))
                else:
                    GL_Result_2[username][reportname][0] += 1
                GL_Result_2[username][reportname][1] += 1
            checkeq = f"{GL_Result_2[username][reportname][0]} / {GL_Result_2[username][reportname][1]}"
            if GL_Result_2[username][reportname][0] == GL_Result_2[username][reportname][1]:
                checkeq = colored(checkeq, 'green')
            else:
                checkeq = colored(checkeq, 'red')
            print_blue(_("  {} {} {}").format(checkeq, colored("REGEXs matched in file", 'blue'), colored(reportname, 'blue', attrs=['bold'])))
        print_blue("\n")
    # TODO: Semantic_check():

def print_regex_record(record):
    print(_(" Re: {}").format(colored(record['regex'], attrs=['bold'])))
    if record['files'] != ['']:
        print(_("   Files ({}put):").format(record['inout']), end="\t")
        for filename in record['files']:
            print(filename, end="\t")
    else:
        print(_("   Every imported file ({}put).").format(record['inout']), end="\t")
    print("")

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

    def emptyline(self):
        """Override: Called when an empty line is entered in response to the prompt."""
        if self.lastcmd:
            self.lastcmd = ""
            return self.onecmd('\n')

    def do_help(self, arg):
        print_help_regex()
        self.lastcmd = ''

    def do_addre(self, arg):
        """Check REPORTs with REGEX"""
        self.lastcmd = ''

    def do_q(self, arg):
        """Easier exit"""
        return True

    def do_exit(self, arg):
        return True
    # TODO: Make cmd history recover after exiting regex mode

class Repl(cmd.Cmd):
    prompt = colored(_("[ NetJu ]:~$ "), 'blue')
    print_cyan(_(" ==[ Welcome to NET-JUDGE - Check enviroment for iproute2 library! ]==\n"))
    lastcmd = ''

    def emptyline(self):
        """Override: Called when an empty line is entered in response to the prompt."""
        if self.lastcmd:
            self.lastcmd = ""
            return self.onecmd('\n')

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
        global GL_Files, GL_Result_1, GL_Result_2, GL_Regex
        GL_Files = GL_Result_1 = GL_Result_2 = defaultdict(dict)
        GL_Regex = []
        print_cyan(_(" ==[ All progress is reset!! ]==\n"))

    def do_importedreports(self, arg):
        """Print imported report files"""
        if not GL_Files:
            print_cyan(_("  =[ No reports imported ]="))
        else:
            print_cyan(_("  =[ Imported reports: ]="))
            for username, userfiles in GL_Files.items():
                print(_("Participant: {} His files:\n\t").format(colored(username, attrs=['bold'])), end="")
                for userfile in userfiles.keys():
                    print(userfile, end="\t ")
                print("")

    def do_importedinstructions(self, arg):
        """Print imported instruction files"""
        if not GL_Regex:
            print_cyan(_("  =[ No instructions imported ]="))
        else:
            print_cyan(_("  =[ Imported instructions: ]="))
            for record in GL_Regex:
                print_regex_record(record)

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
        Instr. files contain regex to check if smth is present in report.
        This information is important for the last step of checking.

        Input: Target directories to extract instructions from.
        Output: List of imported instruction files.
        """
        args = shlex.split(arg, comments=True)
        if len(args) == 0:
            print_red(_("Not enough arguments"))
        else:
            json_path = args[0:]
            import_instructions_from_json(json_path)  

    def do_saveins(self, arg):
        """Save regular expressions in file in json format.

        Input: File path
        """
        args = shlex.split(arg, comments=True)
        if len(args) not in [1]:
            print_red(_("Wrong number of arguments"))
        else:
            try:
                with open(args[0], 'w') as f:
                    json.dump(GL_Regex, f, indent = 6)
            except FileNotFoundError as E:
                print_red(E)
            else:
                print_green(_("Success: Saved REGEXs in {}").format(args[0]))

    def do_addreg(self, arg):
        """AddReg is used to add single regular expression to collection.

        Input: REGEX, in/out, FILE1, FILE2...
        Output: Added regexpr.
        """
        global GL_Regex
        args = shlex.split(arg, comments=True)
        if len(args) < 2:
            print_red(_("Not enough arguments"))
        elif args[1] not in ['in', 'out']:
            print_red(_("Wrong argument {}. Use in/out.").format(args[1]))
        else:
            reg = args[0]
            inout = args[1]
            if len(args) >= 3:
                filenames = args[2:]
            else:
                filenames = ['']
            record = {'regex': reg, 'inout': inout, 'files': filenames}
            GL_Regex.append(record)
            print_green(_('Success'))
            print_regex_record(record)

    def do_regexmode(self, arg):
        """Enter regex mode"""
        args = shlex.split(arg, comments=True)
        print_cyan(_("  ==[ ENTERING REGEX CONSTRUCTOR MODE: ]=="))
        Repl_Regex().cmdloop()
        print_cyan(_("  ==[ EXITING REGEX CONSTRUCTOR MODE: ]=="))
        '''Otherwise last cmd is called after return'''
        self.lastcmd = 'nothing'

    def do_mode(self, arg):
        """Modify verbosity mode"""
        args = shlex.split(arg, comments=True)
        global GL_Mode
        if len(args) != 1:
            print_red(_("Wrong number of arguments"))
        else:
            if args[0] not in ["quiet", "brief", "verbose"]:
                print_red(_('Wrong argument. Use one of "quiet", "brief", "verbose"'))
            else:
                GL_Mode = args[0]
                print_green(_("'{}' mode is set.").format(args[0]))
        self.lastcmd = ''

    def complete_mode(self, text, allcommand, beg, end):
        return [s for s in ["quiet", "brief", "verbose",] if s.startswith(text)]

    def do_start(self, arg):
        """Main function to start checking process. Checking steps:

        1. Parsing & Syntax check;
        2. Semantic check;
        3. Outer semantic check.

        No files in collection:              # # steps done
        Files present in collection:         1 # steps done
        Instructions present in collection:  1 2 steps done

        Input: Number of steps done.
        Output: Result.
        """
        args = shlex.split(arg, comments=True)
        if len(args) not in [0, 1]:
            print_red(_("Wrong number of arguments"))
        else: 
            if len(args) == 1:
                if args[0] not in ["1", "2"]:
                    print_yellow(_("Wrong number of steps to be done: {}").format(args[0]))
                    steps = 0
                else:
                    steps = int(arg[0])
            else:
                steps = 2
            if not GL_Files.keys():
                steps = min(steps, 0)
                print_yellow(_('''No report files imported! => No steps would be done!\nUse \'addf REPORT_USERS_DIR\''''))
            if not GL_Regex:
                steps = min(steps, 1)
                print_yellow(_('''No instructions imported! => Second step is skipped\nUse \'addins INSTRUCTION_FILE\''''))
                print_yellow(_('''Or  \'addreg REGEX, FILE1, FILE2...\''''))

            print_cyan(_("  ==[ CHECK STARTS:  Going through {} steps ]==").format(steps))
            if steps > 0: 
                print_cyan(_("  =[ SYNTAX CHECK ]="))
                Syntax_correct() 
            if steps > 1: 
                print_cyan(_("  =[ SEMANTIC CHECK ]="))
                Semantic_check() 
            print_cyan(_("  ==[ CHECK ENDED ]=="))   

    def complete_start(self, text, allcommand, beg, end):
        return [s for s in ["1", "2",] if s.startswith(text)]

    def do_conclude(self, arg):
        """Function prints general result for each task number presented
        in collection
        """
        print_cyan(_("  ==[ RESULTS ]=="))
        global GL_Result_1, GL_Result_2
        for username, reportdict in GL_Files.items():
            print_blue(colored(_("Participant '{}' results:\n").format(username), attrs=['bold']))
            for reportname, lines in reportdict.items():
                checkeq = f"{GL_Result_2[username][reportname][0]} / {GL_Result_2[username][reportname][1]}"
                if GL_Result_2[username][reportname][0] == GL_Result_2[username][reportname][1]:
                    checkeq = colored(checkeq, 'green')
                else:
                    checkeq = colored(checkeq, 'red')
                print_blue(_("  {}:\t{}").format(reportname, checkeq))
            print("")
        # TODO: Make marks
