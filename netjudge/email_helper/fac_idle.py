"""Fac idle."""
import datetime
import imaplib
import ssl
from time import sleep

from netjudge.email_helper.mailer_configs import *
from netjudge.email_helper.mailer_utilities import *

__all__ = ['fac_idle_main']


def fac_idle_main():
    """Main function."""
    configs = load_configs()

    fac_mailbox = get_fac_mailbox()
    ya_mailbox = get_ya_mailbox()

    fac_mailer_utils = MailerUtilities(fac_mailbox)
    fac_mailer_utils.transfer_mail_to_mailbox_and_archive('all', ya_mailbox,
                                                          configs['Fac Server']['storage folder'],
                                                          configs['Yandex Server']['folder'],
                                                          print_info=True)

    print(f'[{datetime.datetime.now().strftime("%H:%M %d.%m")}] Start IDLE mode')

    while True:
        try:
            responses = fac_mailbox.idle.wait(5 * 60)
            # print(f'[{datetime.datetime.now().strftime("%H:%M %d.%m")}] {responses}')
            recent = [item for item in responses if item.endswith(b'RECENT')]

            if recent:
                fac_mailer_utils.transfer_mail_to_mailbox_and_archive('all', ya_mailbox,
                                                                      configs['Fac Server']['storage folder'],
                                                                      configs['Yandex Server']['folder'],
                                                                      print_info=True)

        except (imaplib.IMAP4.abort, ssl.SSLEOFError):
            try:
                while True:
                    print(f'[{datetime.datetime.now().strftime("%H:%M %d.%m")}] Reconnecting...')
                    fac_mailbox = get_fac_mailbox()
                    ya_mailbox = get_ya_mailbox()

                    fac_mailer_utils = MailerUtilities(fac_mailbox)
                    fac_mailer_utils.transfer_mail_to_mailbox_and_archive('all', ya_mailbox,
                                                                          configs['Fac Server']['storage folder'],
                                                                          configs['Yandex Server']['folder'],
                                                                          print_info=True)
                    break
            except (ConnectionError):
                print(f'[{datetime.datetime.now().strftime("%H:%M %d.%m")}] Reconnecting failed. Timeout 5 minutes')
                sleep(5 * 60)

        except KeyboardInterrupt:
            print(f'[{datetime.datetime.now().strftime("%H:%M %d.%m")}] Exit IDLE mode')
            break
