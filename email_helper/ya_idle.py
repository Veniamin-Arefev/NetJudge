"""Yandex idle."""
import datetime
import imaplib
import ssl
from time import sleep

from email_helper.mailer_configs import *
from email_helper.mailer_utilities import connect_to_mailbox

__all__ = ['ya_idle_main']


def update():
    """Update."""
    print(f'[{datetime.datetime.now().strftime("%H:%M")}] Update!')
    try:
        from email_helper.ya_parse import ya_parse_main
        ya_parse_main()
    except BaseException as e:
        print(e)


def ya_idle_main():
    """Main function."""
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
