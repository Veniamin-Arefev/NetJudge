# <center> **NET JUDGE** </center>
<p align="center">
    <img src="https://img.shields.io/github/languages/count/Veniamin-Arefev/NetJudge"> 
    <img src="https://img.shields.io/github/repo-size/Veniamin-Arefev/NetJudge"> 
    <img src="https://img.shields.io/github/last-commit/Veniamin-Arefev/NetJudge"> 
    <img src="https://img.shields.io/github/commit-activity/m/Veniamin-Arefev/NetJudge">

</p>

### **Net Judge** is a check environment for Linux Network oriented courses. 

Course host may use this project to check how course participants progress solve tasks. **Net Judge** is initially used in [«Working with network protocols in Linux»](http://uneex.ru/LecturesCMC/LinuxNetwork2022) course. The system provides following workflow:

## **Workflow scheme:**

              [TEST KITs]        [REPORTs]            
                   |                 |
                   |                 V
                   |               eMAIL ---> NOTIFICATION TABLE <---+
                   |                 |                               |
                   |                 |                               |
                   |                 | +----- [REPORTs from DIR]     |
                   |                 | |                             |
                   |                 V V                             |
                   |            SYNTAX CHECK ------------------------+
                   |                  |                              |
                   |                  V                              |
                   +--------> SEMANTICS CHECK -----------------------+
                                      |
                                      V
                                  [RESULTS]

- **Test kit** is a file with rules (regular expression) for each task, that determines what insides should report have;
- **Report** is a file with commands executing actions needed to solve the task;
- [**Notification table**](https://uneex.veniamin.space/) (for [this course](http://uneex.ru/LecturesCMC/LinuxNetwork2022)) includes info on current course results;
- **Syntax check** & **Semantics check** are steps needed to estimate task results. Both steps impact in score calculation. While **syntax check** acts mostly to adapt reports to more readable format, **semantics check** uses **Test kit** to check reports. Both steps impact in score calculation
- **Results** are grades for each user and task file.

## **Interface:**

Project interface includes both [**notification table**](https://uneex.veniamin.space/) for course participants, and interactive `command line` for course commander & moderators.

## **Config files:**
Current project uses two config file for work. File names is `mailer_fac.cfg` and `mailer_ya.cfg`.
If you don't have it, you may run any command that interact with mail and create default config file named `mailer.cfg`.

## **Available scripts after installation:**
 * netjudge-fac_idle - Fetch all mail from faculty mail, redirect it to yandex mail and enter idle
 * netjudge-ya_idle - Fetch all mail from yandex mail, update database and enter idle
 * netjudge-download - Download all letters attachments from yandex mail, also support
 * netjudge-database parse - Parse all attachments and populate database
 * netjudge-database export \<FILENAME\> - Export database info info csv file named <FILENAME>
 * netjudge-ya_parse - Create html(actually php) view of database data
 * netjudge-report_analyser - Start cmdline for regex selection(examples listed below)

## **Report analyser usage example:**

The project supports following alternatives:
 * Importing reports from database / local directory;
 * Importing instruction file from local directory;
 * Saving results in database;

Here are some usage examples:
1. Running Net-Judge using reports from database:
```
netjudge-download
netjudge-database
netjudge-report_analyser DATABASE
[ NetJu ]:~$ addins input_example/instruction.json
[ NetJu ]:~$ start 2
[ NetJu ]:~$ conclude
[ NetJu ]:~$ saveres
[ NetJu ]:~$ q
```
## Additional possibillities:
2. Running Net-Judge with one command without database interference:
```
netjudge-report_analyser DIR input_example/ input_example/instruction.json
```
3. Running Net-Judge without database interference:
```
netjudge-report_analyser CMD
[ NetJu ]:~$ addrep input_example
[ NetJu ]:~$ addins input_example/instruction.json
[ NetJu ]:~$ start 2
[ NetJu ]:~$ conclude
[ NetJu ]:~$ saveres input_example/results.json
[ NetJu ]:~$ q
```
4. Testing a regex, then saving it in filesystem:
```
netjudge-report_analyser CMD
[ NetJu ]:~$ addrep input_example
[ NetJu ]:~$ regextest
[ RegexTest ]:~$ re 10 in report.03.base
[ RegexTest ]:~$ re 10 out
[ RegexTest ]:~$ q
[ NetJu ]:~$ addreg 10 in report.03.base
[ NetJu ]:~$ saveins input_example/instr_example.json
[ NetJu ]:~$ q
```
5. Being confused :d
```
netjudge-report_analyser CMD
[ NetJu ]:~$ help
```

## **Dependencies:**

Python libs/modules:
- `bs4`, `sqlalchemy`, `imap_tools`, `termcolor`
- python version >= 3.10

## **Authors:**

- [Dmitry Stamplevsky](https://github.com/stamplevskiyd)
- [Okonishnikov Ariy](https://github.com/Uberariy)
- [Veniamin Arefev](https://github.com/Veniamin-Arefev)
