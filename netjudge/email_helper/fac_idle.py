"""Fac idle."""
import imaplib
import ssl
from time import sleep

from netjudge.common.configs import *
from netjudge.common.logger import get_logger

my_logger = get_logger(__name__, true_name="fac_idle")

from netjudge.email_helper.mailer_utilities import *

__all__ = ['fac_idle_main']


def fac_idle_main():
    """Main function."""
    configs = load_configs()

    timeout_time = int(configs['Fac Server']['timeout time'])

    fac_mailbox = get_fac_mailbox()
    ya_mailbox = get_ya_mailbox()

    fac_mailer_utils = MailerUtilities(fac_mailbox)

    need_update: bool = True

    my_logger.info('Start IDLE mode')

    while True:
        try:
            if need_update:
                fac_mailer_utils.transfer_mail_to_mailbox_and_mark_seen(ya_mailbox,
                                                                        configs['Yandex Server']['folder'],
                                                                        print_info=True)
                need_update = False

            responses = fac_mailbox.idle.wait(timeout_time)

            if [item for item in responses if item.endswith(b'RECENT')]:
                need_update = True


        except (imaplib.IMAP4.abort, ssl.SSLEOFError):
            need_update = True

            while True:
                try:
                    my_logger.warn('Reconnecting...')
                    fac_mailbox = get_fac_mailbox()
                    ya_mailbox = get_ya_mailbox()

                    fac_mailer_utils = MailerUtilities(fac_mailbox)
                    break
                except (ConnectionError):
                    my_logger.warn(f'Reconnecting failed. Timeout {timeout_time} seconds')
                    sleep(timeout_time)


        except KeyboardInterrupt:
            my_logger.info('Exit IDLE mode')
            break
