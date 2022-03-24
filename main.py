from datetime import datetime, timedelta
from imap_tools import MailBox
from mailer_configs import *
from mailer_utilities import *
from table_utilities import *

configs = load_configs()

mailbox = MailBox(configs['Server']['email server host'])
mailbox.login(configs['Credentials']['Username'],
              configs['Credentials']['Password']
              , initial_folder=configs['Server']['folder'])

homeworks = {
    "00_StackVirtualBox": ["image file"],
    "01_HardwareAndCommandline": ["report.01.base", "report.01.clone"],
    "02_DataLink": ["report.02.base", "report.02.clone"],
    "03_BridgeVlan": ["report.03.base", "report.03.clone", "report.03.bridge"],
    "04_AddressAndRoute": ["TODO"],
}


def get_deadlines(keys: list[str], date: list[str]):
    deadlines_format = "%Y-%m-%d %z"
    return_dict = {}
    for index, key in enumerate(keys):
        return_dict[key] = datetime.strptime(date[index] + " +0300", deadlines_format) + timedelta(days=1)
    return return_dict


# noinspection PyTypeChecker
deadlines = get_deadlines(homeworks.keys(), [
    '2022-02-16',
    '2022-02-23',
    '2022-03-02',
    '2022-03-09',
    '2022-03-16',
    '2022-03-23',
    '2022-03-30',
    '2022-04-06',
    '2022-04-13',
    '2022-04-20',
    '2022-04-27',
    '2022-05-04',
])

submitted = {name: list() for name in homeworks}

mailer_utils = MailerUtilities(mailbox)

mailer_names = {}

for homework_name, homework_files in homeworks.items():
    uids = mailer_utils.get_by_filenames(homework_files)
    for mail in mailer_utils.get_by_uids(uids):
        correct_date = datetime.strptime(mail.date_str, "%a, %d %b %Y %H:%M:%S %z")
        submitted[homework_name].append((mail.id,
                                         mail.from_,
                                         correct_date,
                                         correct_date < deadlines[homework_name]))

create_html(submitted)
