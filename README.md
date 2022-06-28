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
You must submit correctly filled config file named `mailer.cfg` for programm. It must contain credentials for faculty's and yandex mails, web server properties and homework info(name, files and deadlines for each). Default config file can be created by running any script.

## **Available scripts after installation:**
 * netjudge-fac_idle - Fetches all mail from faculty `folder` from configs, moves them to `storage folder`, also creates copy for yandex `folder`. After that turns idle mode, that repeats process if new mail arrives.
 * netjudge-ya_idle - Fetches all mail from yandex `folder` from configs, downloads new mail to `tasks` folder, update database with new entries. After that turns idle mode, that repeats process if new mail arrives.
 * netjudge-download - Download all letters attachments from yandex mailbox
 * netjudge-web_server - Download all letters attachments from yandex mail, also support
 * netjudge-database parse - Parse all downloaded files `tasks` folder, then populate database
 * netjudge-database export \<FILENAME\> - Export database info info csv files named <FILENAME> and regex_<FILENAME>
 * netjudge-report_analyser - Start cmdline for regex selection(examples listed below)
 
## **Common use cases:**

0. netjudge-fac_idle program should be run only in one instance at a time. 

1. We want to start web server, that will automatically update everything if new mail arrives.  We need to start 3 separated consoles in background.
    ```
    in first  $ netjudge-fac_idle
    in second $ netjudge-ya_idle
    in third  $ netjudge-web_server
    ```
2. We want to use report_analyser with fac_idle running somewhere. It means that we want to copy all mail from fac mailbox to yandex mailbox first, then download all mail and update database.

    1. We want to continue receiving updates to out database. We should run in background:
        ```
        $ netjudge-ya_idle
        ```
        
    1. We want to download all letters once. We should run:
        ```
        $ netjudge-download
        $ netjudge-database parse
        ```
        
    After creating `data.db` we can run:
    
    ```
    $ netjudge-report_analyser DATABASE
    ```
3. We want to use report_analyser without fac_idle running somewhere. It means that we want to copy all mail from fac mailbox to yandex mailbox first.
We need to run this command in console:
    ```
    $ netjudge-fac_idle
    ```

    Ather it print, that it entered idle mode, we can stop it by pressing ^С. After that we can go to to point 2.

## **Report analyser usage example:**

The project supports following alternatives:
 * Importing reports from database / local directory;
 * Importing instruction file from local directory;
 * Saving results in database;

Here are some usage examples:
1. Running Net-Judge using reports from database:
```
netjudge-download
netjudge-database parse
netjudge-report_analyser DATABASE
[ NetJu ]:~$ addins input_example/instruction.json
[ NetJu ]:~$ start 2
[ NetJu ]:~$ conclude
[ NetJu ]:~$ saveres
[ NetJu ]:~$ q
```
Additional possibillities:

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
[ RegexTest ]:~$ re in 10 report.03.base
[ RegexTest ]:~$ re out 10
[ RegexTest ]:~$ q
[ NetJu ]:~$ addreg in 10 report.03.base
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
- python version >= 3.9

## **Authors:**

- [Dmitry Stamplevsky](https://github.com/stamplevskiyd)
- [Okonishnikov Ariy](https://github.com/Uberariy)
- [Veniamin Arefev](https://github.com/Veniamin-Arefev)
