"""Yandex idle."""
import datetime
import imaplib
import ssl
import os
from time import sleep

from netjudge.email_helper.mailer_utilities import get_ya_mailbox
from netjudge.email_helper.ya_download import ya_download
from netjudge.email_helper.deadlines import homeworks_names_and_files

__all__ = ['ya_idle_main']


def update():
    """Update."""
    print(f'[{datetime.datetime.now().strftime("%H:%M %d.%m")}] Update!')
    try:
        import netjudge.database
        from netjudge.database.functions import add_report, rate_reports
        # path == task_dir/homework_name/email/uid/<files>
        for path in ya_download():
            for filename in homeworks_names_and_files[path.split(os.sep)[1]]:
                add_report(path.split(os.sep)[2], path + os.sep + filename)
        rate_reports(print_info=True)
        with open('last_update_time', 'w') as file:
            file.write(datetime.datetime.now().strftime("%d %b %H:%M"))

    except BaseException as e:
        print(e)


def ya_idle_main():
    """Main function."""
    ya_mailbox = get_ya_mailbox()

    need_update: bool = True

    print(f'[{datetime.datetime.now().strftime("%H:%M %d.%m")}] Start IDLE mode')

    while True:
        try:
            if need_update:
                update()

            responses = ya_mailbox.idle.wait(5 * 60)

            if [item for item in responses if item.endswith(b'RECENT')]:
                need_update = True


        except (imaplib.IMAP4.abort, ssl.SSLEOFError):
            try:
                while True:
                    while True:
                        print(f'[{datetime.datetime.now().strftime("%H:%M %d.%m")}] Reconnecting...')
                        ya_mailbox = get_ya_mailbox()
                        break

                    need_update = True

                    break
            except (ConnectionError):
                print(f'[{datetime.datetime.now().strftime("%H:%M %d.%m")}] Reconnecting failed. Timeout 5 minutes')
                sleep(5 * 60)

        except KeyboardInterrupt:
            print(f'[{datetime.datetime.now().strftime("%H:%M %d.%m")}] Exit IDLE mode')
            break
