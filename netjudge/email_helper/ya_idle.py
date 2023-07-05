"""Yandex idle."""
import datetime
import imaplib
import ssl
import os
from time import sleep

from netjudge.common.configs import load_configs
from netjudge.common.logger import get_logger

my_logger = get_logger(__name__, true_name="ya_idle")

from netjudge.email_helper.mailer_utilities import get_ya_mailbox
from netjudge.email_helper.ya_download import ya_download
from netjudge.common.deadlines import homeworks_names_and_files

__all__ = ['ya_idle_main']


def update():
    """Update."""
    my_logger.info("Update!")
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
        my_logger.error(e)


def ya_idle_main():
    """Main function."""
    configs = load_configs()

    timeout_time = int(configs['Yandex Server']['timeout time'])

    ya_mailbox = get_ya_mailbox()

    need_update: bool = True

    my_logger.info('Start IDLE mode')

    while True:
        try:
            if need_update:
                update()
                need_update = False

            responses = ya_mailbox.idle.wait(timeout_time)

            if [item for item in responses if item.endswith(b'RECENT')]:
                need_update = True


        except (imaplib.IMAP4.abort, ssl.SSLEOFError):
            need_update = True
            while True:
                try:
                    my_logger.warn('Reconnecting...')
                    ya_mailbox = get_ya_mailbox()
                    break
                except (ConnectionError):
                    my_logger.warn(f'Reconnecting failed. Timeout {timeout_time} seconds')
                    sleep(timeout_time)

        except KeyboardInterrupt:
            my_logger.info('Exit IDLE mode')
            break
