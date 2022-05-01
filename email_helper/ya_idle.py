import configparser
import datetime
import imaplib
import ssl
import subprocess
from time import sleep

from imap_tools import MailBox

from email_helper.mailer_configs import *


def connect_to_mailbox(configs: configparser.ConfigParser):
    con_mailbox = MailBox(configs['Server']['email server host'])
    con_mailbox.login(configs['Credentials']['Username'],
                      configs['Credentials']['Password']
                      , initial_folder=configs['Server']['folder'])

    return con_mailbox


def update():
    print(f'[{datetime.datetime.now().strftime("%H:%M")}] Update!')
    my_process = subprocess.run(['python', 'ya_parse.py'])
    if my_process.stderr is not None:
        print(my_process.stderr)


def ya_idle_main():
    ya_configs = load_configs('mailer_ya.cfg')

    ya_mailbox = connect_to_mailbox(ya_configs)
    update()

    print(f'[{datetime.datetime.now().strftime("%H:%M")}] Start IDLE mode')

    while True:
        try:
            responses = ya_mailbox.idle.wait(5 * 60)
            # print(f'[{datetime.datetime.now().strftime("%H:%M")}] {responses}')
            recent = [item for item in responses if item.endswith(b'RECENT')]

            if recent:
                update()

        except (imaplib.IMAP4.abort, ssl.SSLEOFError):
            try:
                while True:
                    print(f'[{datetime.datetime.now().strftime("%H:%M")}] Reconnecting...')
                    ya_mailbox = connect_to_mailbox(ya_configs)
                    break
            except (ConnectionError):
                print(f'[{datetime.datetime.now().strftime("%H:%M")}] Reconnecting failed. Timeout 5 minutes')
                sleep(5 * 60)

            update()

        except KeyboardInterrupt:
            print(f'[{datetime.datetime.now().strftime("%H:%M")}] Exit IDLE mode')
            break
