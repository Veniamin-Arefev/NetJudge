import configparser
import imaplib
import subprocess
from mailer_configs import *
from mailer_utilities import *


def connect_to_mailbox(configs: configparser.ConfigParser):
    con_mailbox = MailBox(configs['Server']['email server host'])
    con_mailbox.login(configs['Credentials']['Username'],
                      configs['Credentials']['Password']
                      , initial_folder=configs['Server']['folder'])

    return con_mailbox


ya_configs = load_configs('mailer_ya.cfg')
ya_mailbox = connect_to_mailbox(ya_configs)

print('Update!')
subprocess.run(['python', 'ya_parse.py'])
print('Start IDLE mode')

ya_mailbox.idle.start()

while True:
    try:
        responses = ya_mailbox.idle.poll(None)
        print(responses)
        recent = [item for item in responses if item.endswith(b'RECENT')]

        # recent_uids = [sub_item.decode() for item in recent for sub_item in item.split() if (sub_item.isdigit())]
        # print(recent_uids)

        if recent:
            print('Update!')
            process = subprocess.run(['python', 'ya_parse.py'])
            print(process.stdout)
            print(process.stderr)
            print(process.returncode)
    except imaplib.IMAP4.abort:
        print('Reconnecting...')
        ya_mailbox = connect_to_mailbox(ya_configs)
        ya_mailbox.idle.start()

    except KeyboardInterrupt:
        print("Exit IDLE mode")
        ya_mailbox.idle.stop()
        break
