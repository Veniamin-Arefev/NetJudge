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
        # workaround because yandex blocks
        i += 1
        if i == 3:
            i = 0
            mailbox = get_ya_mailbox()
            mailer_utils = MailerUtilities(mailbox)
        if print_info:
            print(f"Current parsing task : {homework_name:>30}.", end=" ")
        uids = mailer_utils.get_by_filenames(homework_files)
        submitted[homework_name] = uids
        if print_info:
            print(f"Found : {len(uids):5} mails")

    if not os.path.isdir(download_dir):
        os.mkdir(download_dir)

    success_downloaded = []

    for homework_name, homeworks_files in homeworks_names_and_files.items():
        if print_info:
            print(f"Current downloading task : {homework_name:>30}.")
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

    print(f"Downloaded total of {len(success_downloaded)} files")
    print(f"Fixing reports...")
    report_fixer(download_dir)
    return success_downloaded
