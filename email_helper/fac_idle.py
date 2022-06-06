import datetime
import imaplib
import ssl
from time import sleep

from email_helper.mailer_configs import *
from email_helper.mailer_utilities import *

__all__ = ['fac_idle_main']


def fac_idle_main():
    fac_configs = load_configs('mailer_fac.cfg')
    ya_configs = load_configs('mailer_ya.cfg')

    fac_mailbox = connect_to_mailbox(fac_configs)
    ya_mailbox = connect_to_mailbox(ya_configs)

    fac_mailer_utils = MailerUtilities(fac_mailbox)
    fac_mailer_utils.transfer_mail_to_mailbox_and_archive('all', ya_mailbox, print_info=True)

    print(f'[{datetime.datetime.now().strftime("%H:%M")}] Start IDLE mode')

    while True:
        try:
            responses = fac_mailbox.idle.wait(5 * 60)
            # print(f'[{datetime.datetime.now().strftime("%H:%M")}] {responses}')
            recent = [item for item in responses if item.endswith(b'RECENT')]

            if recent:
                fac_mailer_utils.transfer_mail_to_mailbox_and_archive('all', ya_mailbox, print_info=True)

        except (imaplib.IMAP4.abort, ssl.SSLEOFError):
            try:
                while True:
                    print(f'[{datetime.datetime.now().strftime("%H:%M")}] Reconnecting...')
                    fac_mailbox = connect_to_mailbox(fac_configs)
                    ya_mailbox = connect_to_mailbox(ya_configs)

                    fac_mailer_utils = MailerUtilities(fac_mailbox)
                    fac_mailer_utils.transfer_mail_to_mailbox_and_archive('all', ya_mailbox, print_info=True)
                    break
            except (ConnectionError):
                print(f'[{datetime.datetime.now().strftime("%H:%M")}] Reconnecting failed. Timeout 5 minutes')
                sleep(5 * 60)

        except KeyboardInterrupt:
            print(f'[{datetime.datetime.now().strftime("%H:%M")}] Exit IDLE mode')
            break
