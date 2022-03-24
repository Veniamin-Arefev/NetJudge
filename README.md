# <center> **NET JUDGE** </center>
<p align="center">
    <img src="https://img.shields.io/github/languages/count/Veniamin-Arefev/NetJudge"> 
    <img src="https://img.shields.io/github/repo-size/Veniamin-Arefev/NetJudge"> 
    <img src="https://img.shields.io/github/last-commit/Veniamin-Arefev/NetJudge"> 
    <img src="https://img.shields.io/github/commit-activity/m/Veniamin-Arefev/NetJudge">

</p>

### **Net Judge** is a check enviroment for CS MSU course [«Working with network protocols in Linux»](http://uneex.ru/LecturesCMC/LinuxNetwork2022). The system provides following workflow:

## **Workflow scheme:**

              [TEST KITs]        [REPORTs]            
                   |                 |
                   |                 V
                   |               eMAIL ---> NOTIFICATION TABLE <---+
                   |                 |                               |
                   |                 V                               |
                   |              PARSING                            |
                   |                 |                               |
                   |                 V                               |
                   |            SYNTAX CHECK ------------------------+
                   |                 |                               |
                   |                 V                               |
                   +--------> SEMANTICS CHECK -----------------------+
                                     |
                                     V
                                 [RESULTS]

- **Test kit** is a file with rules for each task, that determines what insides should report have;
- **Report** is a file with commands executing actions needed to solve the task;
- [**Notification table**](https://uneex.veniamin.space/) includes info on current course results;
- **Syntax check** & **Semantics check** are steps needed to estimate task results. Both steps impact in score calculation;
- **Results** are grades for each task.

## **Dependencies:**

Python libs/modules:
- `beautifulsoup4`, `re`, `textdistance`, `shlex`, `tarfile`, `configparser`
## **Interface:**

Project interface includes both [**notification table**](https://uneex.veniamin.space/) for course participants, and interactive `command line` for course commander & moderators.

## **Authors:**

- [Veniamin Arefev](https://github.com/Veniamin-Arefev)
- [Okonishnikov Ariy](https://github.com/Uberariy)
- [Dmitry Stamplevsky](https://github.com/stamplevskiyd)
