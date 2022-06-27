"""Yandex downloader."""
import os
from netjudge.email_helper.mailer_utilities import *
from netjudge.email_helper.deadlines import *
from netjudge.email_helper.report_fixer import report_fixer

__all__ = ['ya_download']


def ya_download(download_dir='tasks', print_info=True):
    """Download."""

    mailbox = get_ya_mailbox()
    mailer_utils = MailerUtilities(mailbox)

    submitted = {}

    i = 0
    for homework_name, homework_files in homeworks_names_and_files.items():
        i += 1
        if i == 3:
            i = 0
            mailbox = get_ya_mailbox()
            mailer_utils = MailerUtilities(mailbox)
        if print_info:
            print(f"Current parsing task : {homework_name}", end=' ' * 40 + '\r')
        uids = mailer_utils.get_by_filenames(homework_files)
        submitted[homework_name] = uids

    if not os.path.isdir(download_dir):
        os.mkdir(download_dir)

    success_downloaded = []

    for homework_name, homeworks_files in homeworks_names_and_files.items():
        if print_info:
            print(f"Current download task : {homework_name}", end=' ' * 40 + '\r')
        cur_dir = download_dir + os.sep + homework_name
        if not os.path.isdir(cur_dir):
            os.mkdir(cur_dir)

        for mail in mailer_utils.get_by_uids(submitted[homework_name]):
            email_path = cur_dir + os.sep + mail.from_
            if not os.path.isdir(email_path):
                os.mkdir(email_path)
            email_path += os.sep + mail.uid
            if os.path.exists(email_path):
                continue
            os.mkdir(email_path)
            for attachment in mail.attachments:
                if attachment.filename in homeworks_files:
                    with open(email_path + os.sep + attachment.filename, 'wb') as f:
                        f.write(attachment.payload)
            success_downloaded.append(email_path)
    report_fixer(download_dir)
    return success_downloaded
