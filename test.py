import imaplib
import os
from datetime import datetime, timedelta
from email.header import decode_header

from imap_tools import MailBox, AND

from mailer_configs import *
from mailer_utilities import *

configs = load_configs('mailer_ya.cfg')

mailbox = MailBox(configs['Server']['email server host'])
mailbox.login(configs['Credentials']['Username'],
              configs['Credentials']['Password']
              , initial_folder=configs['Server']['folder'])

homeworks = {
    "00_StackVirtualBox": ["image file"],
    "01_HardwareAndCommandline": ["report.01.base", "report.01.clone"],
    "02_DataLink": ["report.02.base", "report.02.clone"],
    "03_BridgeVlan": ["report.03.base", "report.03.clone", "report.03.bridge"],
    "04_AddressAndRoute": ['report.04.base', 'report.04.clone', 'report.04.router1', 'report.04.router2'],
    "05_IProuteRule": ['report.05.router', 'report.05.client1', 'report.05.client2'],
    "06_TransportAndNAT": ['TODO'],
    "07_ApplicationSystem": ['TODO'],
    "08_ApplicationSupplemental": ['TODO'],
    "09_NetworkProtocolsSecurity": ['TODO'],
    "10_SecurityAndTools": ['TODO'],
    "11_FireWalls": ['TODO'],
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
    '2022-03-18',
    '2022-03-23',
    '2022-03-30',
    '2022-04-06',
    '2022-04-13',
    '2022-04-20',
    '2022-04-27',
    '2022-05-04',
])
