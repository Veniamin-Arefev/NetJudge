from datetime import datetime
from email.header import decode_header

import email_helper.mailer_utilities
from email_helper.mailer_configs import *
from email_helper.mailer_utilities import *
from email_helper.table_utilities import *
from email_helper.deadlines import *

__all__ = ['ya_parse_main']


def ya_parse_main(print_info=False):
    configs = load_configs('mailer_ya.cfg')

    mailbox = email_helper.mailer_utilities.connect_to_mailbox(configs)

    submitted = {name: list() for name in homeworks_names_and_files}

    mailer_utils = MailerUtilities(mailbox)

    mailer_names = {}

    for homework_name, homework_files in homeworks_names_and_files.items():
        if print_info:
            print(f"Current task : {homework_name}", end="\r")
        uids = mailer_utils.get_by_filenames(homework_files)
        for mail in mailer_utils.get_by_uids(uids):
            name = mail.headers['from'][0]
            name, codec = decode_header(name[:name.index('<')].strip())[0]
            if codec is not None:
                mailer_names[mail.from_] = name.decode(codec).title()
            else:
                mailer_names[mail.from_] = name.title()

            correct_date = datetime.strptime(mail.date_str, "%a, %d %b %Y %H:%M:%S %z")
            submitted[homework_name].append((mail.uid,
                                             mail.from_,
                                             correct_date,
                                             correct_date < deadlines[homework_name]))

    create_html(submitted, mailer_names, target_path=configs['Output']['Path to directory'],
                target_filename=configs['Output']['File name'])
