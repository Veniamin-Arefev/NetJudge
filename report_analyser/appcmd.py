"""Commandline functions"""
import locale
import shlex
import cmd
import gettext
import json
from database.functions import *
from collections import defaultdict
from termcolor import colored, cprint

"""Project l10n & i18n"""
translation = gettext.translation('netjudge', 'report_analyser/po', fallback=True)
_, ngettext = translation.gettext, translation.ngettext

"""Cmd colors"""
print_cyan = lambda x: cprint(x, 'cyan')
""" For standart system output"""
print_green = lambda x: cprint(x, 'green')
""" For positive user experience"""
print_red = lambda x: cprint(x, 'red')
""" For negative user experience"""
print_yellow = lambda x: cprint(x, 'yellow')
""" For undefined user experience"""
print_blue = lambda x: cprint(x, 'blue')
""" Standart prompt"""
print_magenta = lambda x: cprint(x, 'magenta')
""" Regex prompt"""


"""Global structures"""
GL_Files = defaultdict(dict)
GL_Result_1 = defaultdict(dict)
GL_Result_2 = defaultdict(dict)
GL_Regex = []
RegexPlay_Regex = []
GL_DataBase = []
GL_Mode = "verbose"
GL_Source = "dir"
GL_IsImported = False


def import_files_from_dir(dir_paths):
    """Add keys to GF_Files"""
    global GL_Source
    GL_Source = "dir"
    once = True
    for dir_path in dir_paths:
        """Find all dirs = users"""
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
                if not checkname[1].isdigit():
                    print_red(f"ERROR: Wrong file format \'{filename}\'. Report number should be integer!")
                    continue
                print(colored(user_dir, attrs=['bold']), " ", filename)
                GL_Files[user_dir][filename] = ""
                GL_Result_2[user_dir][filename] = [0, 0]
        if once:
            print_red(_('No such file or directory'))
    GL_IsImported = False


def import_files_from_base():
    """Add keys to GF_Files"""
    global GL_Source, GL_DataBase
    GL_Source = "database"
    GL_DataBase = collect_data()
    for user in GL_DataBase:
        """Iterate by users. Each user is dict"""
        for task in user['tasks']:
            for report in task['reports']:
                checkname = report['name'].split(".")
                if checkname[0] != "report":
                    print_red(f"ERROR: Wrong file format \'{report['name']}\'. It should start with \'report\'!")
                    continue
                if not checkname[1].isdigit():
                    print_red(f"ERROR: Wrong file format \'{report['name']}\'. Report number should be integer!")
                    continue
                print(colored(user['email'] + " " + user['name'], attrs=['bold']), " ", report['name'])
                GL_Files[user['email'] + " " + user['name']][report['name']] = ""
                GL_Result_2[user['email'] + " " + user['name']][report['name']] = [0, 0]
    GL_IsImported = False


def import_instructions_from_json(json_paths):
    """Add keys to GF_Instr"""
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
                except Exception:
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


def Syntax_correct(source, mode):
    """Parse files & Write score in GL_Result_1"""
    global GL_IsImported
    for user_dir, userfiles in GL_Files.items():
        if mode != "quiet":
            print("Participant: '", user_dir, "', his files:")
        for userfile in userfiles.keys():
            filename = user_dir + "/" + userfile
            if mode != "quiet":
                print("\t", filename)
            if source == "dir":
                obj = tarfile.open(filename)
                text = obj.extractfile('./OUT.txt').read().decode()
            else:
                text = get_report_text(userfile, user_dir.split()[0], user_dir.split()[1])
            text = re.sub('\r', '', text)
            try:
                lines = [translate(line) for line in text.split('\n') if line]
                GL_Files[user_dir][userfile] = lines
                GL_Result_1[user_dir][userfile] = [1, 1]
            except Exception:
                GL_Result_1[user_dir][userfile] = [0, 1]
    GL_IsImported = True


def Semantic_check(GFiles, GRegex, save_results, mode):
    """Write score in GL_Result_2"""
    global GL_Result_2
    for username, reportdict in GFiles.items():
        once_user = True
        for reportname, lines in reportdict.items():
            regexlist = [regex for regex in GRegex if reportname in regex['files'] or regex['files'] == ['']]
            initialized = False
            once_report = True
            for regexind, regex in enumerate(regexlist):
                if once_user and (mode != 'quiet'):
                    print_blue(colored(_("Checking participant '{}':").format(username), attrs=['bold']))
                    once_user = False
                if once_report and (mode != 'quiet'):
                    print_blue(_("\n  Checking file {}:").format(reportname))
                    once_report = False
                if mode != "quiet":
                    print_cyan(_("    RE {}: '{}' ({}put).").format(regexind, regex['regex'], regex['inout']))
                find = False
                matchind = 0
                linenumber = 0
                for lineind, line in enumerate(lines):
                    if line[0].startswith(regex['inout']):
                        patt = re.compile(regex['regex'])
                        for match in patt.findall(line[1]):
                            find = True
                            matchind += 1
                            if mode != "quiet":
                                print(
                                "      " + colored(_("Match {} in line {}:").format(matchind, lineind), attrs=["bold"]))
                            linewithmatch = colored(match, "green", attrs=["underline"]).join(line[1].split(match))
                            if mode != "quiet":
                                print(_("        {}").format(colored(linewithmatch)))
                            linenumber = lineind + 1
                listed_results = [0, 0]
                initialized = True
                if not find and (mode != 'quiet'):
                    print_red(_("      No matches in {} lines!").format(linenumber))
                else:
                    listed_results[0] += 1
                listed_results[1] += 1
                if initialized:
                    checkeq = f"{listed_results[0]} / {listed_results[1]}"
                    if listed_results[0] == listed_results[1]:
                        checkeq = colored(checkeq, 'green')
                    else:
                        checkeq = colored(checkeq, 'red')
                    if mode != "quiet":
                        print_blue(_("  {} {} {}").format(checkeq, colored("REGEXs matched in file", 'blue'),
                                                        colored(reportname, 'blue', attrs=['bold'])))
                    if save_results:
                        for i in range(0, 2):
                            GL_Result_2[username][reportname][i] += listed_results[i]
        if mode != "quiet":
            print_blue("\n")


def print_regex_record(record):
    """Print file result."""
    print(_(" Re: {}").format(colored(record['regex'], attrs=['bold'])))
    if record['files'] != ['']:
        print(_("   Files ({}put):").format(record['inout']), end="\t")
        for filename in record['files']:
            print(filename, end="\t")
    else:
        print(_("   Every imported file ({}put).").format(record['inout']), end="\t")
    print("")


def print_exit_message():
    """Exit message."""
    print_cyan(_("\n ==[ Exiting! ]=="))


class Repl_Regex(cmd.Cmd):
    """Regex repl class."""

    prompt = colored(_("[ RegexTest ]:~$ "), 'magenta')
    mode = "verbose"

    def emptyline(self):
        """Override: Called when an empty line is entered in response to the prompt."""
        if self.lastcmd:
            self.lastcmd = ""
            return self.onecmd('\n')

    def do_re(self, arg):
        """Test regex on imported reports in regextest mode.

        Usage: re [REGEX] ['in'/'out'] {[FILE]}
           or: re [REGEX] ['in'/'out']

        Add a REGEX and specify, if 'in'-put or 'out'-put of FILEs is checked.
        If FILE is not set, every imported file is checked with this regex!
        REGEX and 'in'/'out' parameters must be set!

        Note, that in 'regextest' mode, results are not saved, only displayed.
        """
        global RegexPlay_Regex, GL_Files, GL_IsImported
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
            RegexPlay_Regex.append(record)
            print_green(_('Testing regex:'))
            print_regex_record(record)
            if not GL_IsImported:
                Syntax_correct(GL_Source, "quiet")
            print_cyan(_("  =[ CHECKING... ]="))
            Semantic_check(GL_Files, RegexPlay_Regex, save_results=False, mode="verbose")
            print_cyan(_("  ==[ CHECK ENDED ]=="))
            RegexPlay_Regex = []

    def do_q(self, arg):
        """Easier exit from regex testing mode.

        Usage: q
        """
        return True

    def do_exit(self, arg):
        """Exit regex testing mode.

        Usage: exit
        """
        return True


class Repl(cmd.Cmd):
    """Main cmd class."""

    prompt = colored(_("[ NetJu ]:~$ "), 'blue')
    print_cyan(_(" ==[ Welcome to NET-JUDGE - Check enviroment for iproute2 library! ]==\n"))
    lastcmd = ''

    def emptyline(self):
        """Override: Called when an empty line is entered in response to the prompt."""
        if self.lastcmd:
            self.lastcmd = ""
            return self.onecmd('\n')

    def do_q(self, arg):
        """Shorter variant of 'exit' command.

        Usage: q
        """
        print_exit_message()
        return True

    def do_exit(self, arg):
        """Exit application. All unsaved data would be lost!

        Usage: exit
        """
        print_exit_message()
        return True

    def do_reset(self, arg):
        """Function that clears all results achieved and imports made.

        Usage: reset
        """
        global GL_Files, GL_Result_1, GL_Result_2, GL_Regex, GL_DataBase, RegexPlay_Regex
        GL_Files = defaultdict(dict)
        GL_Result_1 = defaultdict(dict)
        GL_Result_2 = defaultdict(dict)
        RegexPlay_Regex = []
        GL_DataBase = []
        GL_Regex = []
        print_cyan(_(" ==[ All progress is reset!! ]==\n"))

    def do_importedreports(self, arg):
        """Print imported report files.

        Usage: impoertedreports
        """
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
        """Print imported instruction files

        Usage: importedinstructions
        """
        if not GL_Regex:
            print_cyan(_("  =[ No instructions imported ]="))
        else:
            print_cyan(_("  =[ Imported instructions: ]="))
            for record in GL_Regex:
                print_regex_record(record)

    def do_addrep(self, arg):
        """Add files to check to the collection from 1 or more dirs.

        Usage: addrep {[DIR]}

        Scheme of directory:
            [DIR]---[USER1]---[REPORT1]
                  |         |
                  |         |-[REPORT2]
                  |
                  |-[USER2]---[REPORT1]
        """
        args = shlex.split(arg, comments=True)
        if len(args) == 0:
            print_red(_("Not enough arguments"))
        else:
            dir_paths = args[0:]
            import_files_from_dir(dir_paths)

    def do_addins(self, arg):
        """Add 1 or more instruction files to the regex collection.

        Usage: addins {[FILE]}

        Instr. files contain regex to check if smth is present in report.
        """
        args = shlex.split(arg, comments=True)
        if len(args) == 0:
            print_red(_("Not enough arguments"))
        else:
            json_path = args[0:]
            import_instructions_from_json(json_path)

    def do_saveins(self, arg):
        """Save regular expressions imported in project in file in json format.

        Usage: saveins [FILE]

        If file is present, it will be overrided, otherwise, we create new file
        """
        args = shlex.split(arg, comments=True)
        if len(args) not in [1]:
            print_red(_("Wrong number of arguments"))
        else:
            try:
                with open(args[0], 'w') as f:
                    json.dump(GL_Regex, f, indent=6)
            except FileNotFoundError as E:
                print_red(E)
            else:
                print_green(_("Success: Saved REGEXs in {}").format(args[0]))

    def do_addreg(self, arg):
        """Add a single regular expression to collection.

        Usage: addreg [REGEX] ['in'/'out'] {[FILE]}
           or: addreg [REGEX] ['in'/'out']

        Add a REGEX and specify, if 'in'-put or 'out'-put of FILEs is checked.
        If FILE is not set, every imported file is checked with this regex!
        REGEX and 'in'/'out' parameters must be set!
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

    def do_regextest(self, arg):
        """Enter regex mode and test your regex :)

        Usage: regextest
        """
        print_cyan(_("  ==[ ENTERING REGEX TESTING MODE: ]=="))
        Repl_Regex().cmdloop()
        print_cyan(_("  ==[ EXITING REGEX TESTING MODE: ]=="))
        """Otherwise last cmd is called after return"""
        self.lastcmd = 'nothing'

    def do_mode(self, arg):
        """Modify verbosity mode mode:

        ['quiet'/'verbose']
        """
        args = shlex.split(arg, comments=True)
        global GL_Mode
        if len(args) != 1:
            print_red(_("Wrong number of arguments"))
        else:
            if args[0] not in ["quiet", "verbose"]:
                print_red(_('Wrong argument. Use one of "quiet", "verbose"'))
            else:
                GL_Mode = args[0]
                print_green(_("'{}' mode is set.").format(args[0]))
        self.lastcmd = ''

    def complete_mode(self, text, allcommand, beg, end):
        """Mode."""
        return [s for s in ["quiet", "verbose", ] if s.startswith(text)]

    def do_start(self, arg):
        """Main function to start checking process. Checking steps:

        Usage: start ['1'/'2']

        1. Parsing & Syntax check;
        2. Parsing & Syntax check & Semantic check.

        No files in collection:              # # steps done
        Files present in collection:         1 # steps done
        Instructions present in collection:  1 2 steps done

        Results are saved and can be shown with 'conclude'.
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
                print_yellow(
                    _('''No report files imported! => No steps would be done!\nUse \'addf REPORT_USERS_DIR\''''))
            if not GL_Regex:
                steps = min(steps, 1)
                print_yellow(
                    _('''No instructions imported! => Second step is skipped\nUse \'addins INSTRUCTION_FILE\''''))
                print_yellow(_('''Or  \'addreg REGEX, FILE1, FILE2...\''''))

            print_cyan(_("  ==[ CHECK STARTS:  Going through {} steps ]==").format(steps))
            if steps > 0:
                print_cyan(_("  =[ SYNTAX CHECK ]="))
                if not GL_IsImported:
                    Syntax_correct(GL_Source, GL_Mode)
            if steps > 1:
                print_cyan(_("  =[ SEMANTIC CHECK ]="))
                global GL_Result_2
                Semantic_check(GL_Files, GL_Regex, save_results=True, mode="verbose")
            print_cyan(_("  ==[ CHECK ENDED ]=="))

    def complete_start(self, text, allcommand, beg, end):
        """Start."""
        return [s for s in ["1", "2", ] if s.startswith(text)]

    def do_conclude(self, arg):
        """Function prints general result for each task number presented in collection, and saves this data.

        Usage: conclude
        Note, that conclude accumulates all the results during application run, except
        those made in 'regextest' mode.
        """
        print_cyan(_("  ==[ RESULTS ]=="))
        global GL_Result_1, GL_Result_2, GL_Source, GL_DataBase
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

    def do_saveres(self, arg):
        """Save results. If NetJudge is called with DATABASE argument, there is no need to specify arguments,
        contrariwise, if it is called with DIR or CMD argument, you must write output file for results.
        Usage: saveres {[FILE]}
        """
        global GL_Result_1, GL_Result_2, GL_Source, GL_DataBase
        if GL_Source == "database":
            session = session_factory()
            for user in GL_DataBase:
                for task in user['tasks']:
                    database_task = session.query(Task).get(task['id'])
                    database_task.regex_passed = 0
                    database_task.regex_total = 0
                    for report in task['reports']:
                        regex_score = GL_Result_2[user['email'] + " " + user['name']][report['name']]
                        database_report = session.query(Report).get(report['id'])
                        database_report.regex_passed = regex_score[0]
                        database_report.regex_total = regex_score[1]
                        database_task.regex_passed += regex_score[0]
                        database_task.regex_total += regex_score[1]
                        session.commit()
            session.close()
        else:
            args = shlex.split(arg, comments=True)
            if len(args) not in [1]:
                print_red(_("Wrong number of arguments"))
            else:
                try:
                    with open(args[0], 'w') as f:
                        GL_Result_2["participant name"]["report name"] = ["current grade", "maximum grade"]
                        json.dump(GL_Result_2, f, indent=6)
                except FileNotFoundError as E:
                    print_red(E)
                else:
                    print_green(_("Success: Saved results in {}").format(args[0]))
