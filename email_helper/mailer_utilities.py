import imaplib
import datetime
from email.mime.text import MIMEText
from typing import Union

from imap_tools import MailBox, AND, OR

__all__ = ['MailerUtilities']


class MailerUtilities:
    mailbox: MailBox = None

    def __init__(self, mailbox):
        self.mailbox = mailbox

    @staticmethod
    def encode_mime_header_filename(filename: str):
        msg = MIMEText(filename, 'plain', 'utf-8')
        return msg.as_string().split()[-1]

    def get_uids_for_file(self, filename):
        criteria = f'HEADER Content-Disposition "{filename}"'
        criteria_encoded = f'HEADER Content-Disposition "{self.encode_mime_header_filename(filename)}"'
        return set(self.mailbox.uids(str(OR(criteria, criteria_encoded))))

    def get_by_filenames(self, filenames: list[str]):
        uids = []
        for file in filenames:
            uids.append(self.get_uids_for_file(file))
        return set.intersection(*uids)

    def get_by_uids(self, uids: list[str]):
        return self.mailbox.fetch(AND(uid=",".join(uids)), bulk=True) if len(uids) > 0 else ()

    def transfer_mail_to_mailbox_and_archive(self, uids: Union["all", str, list[str]], target_mailbox: MailBox,
                                             print_info=False):
        if uids == 'all':
            mails = self.mailbox.fetch(AND(all=True), bulk=True, mark_seen=False)
        elif type(uids) == str:
            mails = self.get_by_uids([uids])
        elif type(uids) == list:
            mails = self.get_by_uids(uids)
        else:
            raise ValueError('Bad argument')

        uids_to_move = []
        for mail in mails:
            target_mailbox.append(mail, dt=datetime.datetime.strptime(mail.date_str, "%a, %d %b %Y %H:%M:%S %z"))
            uids_to_move.append(mail.uid)
        self.mailbox.move(uids_to_move, 'archived')

        if print_info and len(uids_to_move) > 0:
            print(f'[{datetime.datetime.now().strftime("%H:%M")}] '
                  f'A total of {len(uids_to_move)} letters have been moved.')
