import configparser
import datetime
import imaplib
import subprocess
from imap_tools import MailBox

from mailer_configs import *


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


ya_configs = load_configs('mailer_ya.cfg')
ya_mailbox = connect_to_mailbox(ya_configs)

update()

print(f'[{datetime.datetime.now().strftime("%H:%M")}] Start IDLE mode')
ya_mailbox.idle.start()

while True:
    try:
        responses = ya_mailbox.idle.poll(None)
        recent = [item for item in responses if item.endswith(b'RECENT')]

        # recent_uids = [sub_item.decode() for item in recent for sub_item in item.split() if (sub_item.isdigit())]
        # print(recent_uids)

        if recent:
            update()


    except imaplib.IMAP4.abort:
        print(f'[{datetime.datetime.now().strftime("%H:%M")}] Reconnecting...')
        ya_mailbox = connect_to_mailbox(ya_configs)
        ya_mailbox.idle.start()

        update()

    except KeyboardInterrupt:
        print(f'[{datetime.datetime.now().strftime("%H:%M")}] Exit IDLE mode')
        ya_mailbox.idle.stop()
        break
