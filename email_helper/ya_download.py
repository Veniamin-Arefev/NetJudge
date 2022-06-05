import os
from email.header import decode_header
from imap_tools import MailBox

from email_helper.mailer_configs import *
from email_helper.mailer_utilities import *
from email_helper.deadlines import *

__all__ = ['ya_download']


def ya_download(download_dir='tasks', print_info=False):
    configs = load_configs('mailer_ya.cfg')

    mailbox = MailBox(configs['Server']['email server host'])
    mailbox.login(configs['Credentials']['Username'],
                  configs['Credentials']['Password']
                  , initial_folder=configs['Server']['folder'])

    submitted = {name: list() for name in homeworks_names_and_files}

    mailer_utils = MailerUtilities(mailbox)

    mailer_names = {}

    for homework_name, homework_files in homeworks_names_and_files.items():
        if print_info:
            print(f"Current parsing task : {homework_name}", end="\r")
        uids = mailer_utils.get_by_filenames(homework_files)
        for mail in mailer_utils.get_by_uids(uids):
            name = mail.headers['from'][0]
            name, codec = decode_header(name[:name.index('<')].strip())[0]
            if codec is not None:
                mailer_names[mail.from_] = name.decode(codec).title()
            else:
                mailer_names[mail.from_] = name.title()

            submitted[homework_name].append((mail.from_, mail.uid))

    try:
        os.mkdir(download_dir)
    except FileExistsError:
        pass

    for homework_name in homeworks_names_and_files.keys():
        if print_info:
            print(f"Current download task : {homework_name}", end="\r")
        cur_dir = download_dir + os.sep + homework_name
        try:
            os.mkdir(cur_dir)
        except FileExistsError:
            pass
        for email, uid in submitted[homework_name]:
            email_path = cur_dir + os.sep + email
            try:
                os.mkdir(email_path)
            except FileExistsError:
                pass
            try_number = 1
            while os.path.isdir(email_path + os.sep + str(try_number)):
                try_number += 1
            email_path += os.sep + str(try_number)
            os.mkdir(email_path)
            for mail in mailer_utils.get_by_uids([uid]):
                for attac in mail.attachments:
                    with open(email_path + os.sep + attac.filename, 'wb') as f:
                        f.write(attac.payload)