import configparser
import imaplib
from mailer_configs import *
from mailer_utilities import *


def connect_to_mailbox(configs: configparser.ConfigParser):
    con_mailbox = MailBox(configs['Server']['email server host'])
    con_mailbox.login(configs['Credentials']['Username'],
                      configs['Credentials']['Password']
                      , initial_folder=configs['Server']['folder'])

    return con_mailbox


fac_configs = load_configs('mailer_fac.cfg')
ya_configs = load_configs('mailer_ya.cfg')

fac_mailbox = connect_to_mailbox(fac_configs)
ya_mailbox = connect_to_mailbox(ya_configs)

fac_mailer_utils = MailerUtilities(fac_mailbox)
fac_mailer_utils.transfer_mail_to_mailbox_and_archive('all', ya_mailbox, print_info=True)

print('Start IDLE mode')

while True:
    try:
        responses = fac_mailbox.idle.wait(None)
        # print(responses)
        recent = [item for item in responses if item.endswith(b'RECENT')]
        # recent_uids = [sub_item.decode() for item in recent for sub_item in item.split() if (sub_item.isdigit())]
        # print(recent_uids)

        if recent:
            fac_mailer_utils.transfer_mail_to_mailbox_and_archive('all', ya_mailbox, print_info=True)

    except imaplib.IMAP4.abort:
        print('Reconnecting...')
        fac_mailbox = connect_to_mailbox(fac_configs)
        ya_mailbox = connect_to_mailbox(ya_configs)

        fac_mailer_utils = MailerUtilities(fac_mailbox)
    except KeyboardInterrupt:
        print("Exit IDLE mode")
        # fac_mailbox.idle.stop()
        break
