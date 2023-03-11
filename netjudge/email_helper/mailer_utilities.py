"""Mail utilities."""
import datetime
from email.mime.text import MIMEText
from email.header import decode_header
from imap_tools import MailBox, AND, OR

__all__ = ['MailerUtilities', 'get_ya_mailbox', 'get_fac_mailbox']

from .mailer_configs import load_configs


def get_ya_mailbox():
    """Get Yandex mailbox."""
    configs = load_configs('mailer.cfg')
    con_mailbox = MailBox(configs['Yandex Server']['email server host'])
    con_mailbox.login(configs['Yandex Credentials']['Username'],
                      configs['Yandex Credentials']['Password'])
    try:
        con_mailbox.folder.create(configs['Yandex Server']['folder'])
    except Exception:
        pass
    con_mailbox.folder.set(configs['Yandex Server']['folder'])
    return con_mailbox


def get_fac_mailbox():
    """Get Fac mailbox."""
    configs = load_configs('mailer.cfg')
    con_mailbox = MailBox(configs['Fac Server']['email server host'])
    con_mailbox.login(configs['Fac Credentials']['Username'],
                      configs['Fac Credentials']['Password'])
    try:
        con_mailbox.folder.create(configs['Fac Server']['folder'])
    except Exception:
        pass
    con_mailbox.folder.set(configs['Fac Server']['folder'])
    try:
        con_mailbox.folder.create(configs['Fac Server']['storage folder'])
    except Exception:
        pass
    return con_mailbox


class MailerUtilities:
    """Mail class."""

    mailbox: MailBox = None

    def __init__(self, mailbox):
        """Initialise class."""
        self.mailbox = mailbox

    @staticmethod
    def encode_mime_header_filename(filename: str):
        """Encode filename."""
        msg = MIMEText(filename, 'plain', 'utf-8')
        return msg.as_string().split()[-1]

    def get_uids_for_file(self, filename):
        """Get uids."""
        criteria = f'HEADER Content-Disposition "{filename}"'
        criteria_encoded = f'HEADER Content-Disposition "{self.encode_mime_header_filename(filename)}"'
        return set(self.mailbox.uids(str(OR(criteria, criteria_encoded))))

    def get_by_filenames(self, filenames: list):
        """Get by filenames."""
        uids = []
        for file in filenames:
            uids.append(self.get_uids_for_file(file))
        return set.intersection(*uids)

    def get_by_uids(self, uids: list, headers_only=False, mark_seen=False):
        """Get by uids."""
        return self.mailbox.fetch(AND(uid=",".join(uids)), bulk=True, headers_only=headers_only,
                                  mark_seen=mark_seen) if len(uids) > 0 else ()

    def get_username_by_email(self, email: str):
        """Get student's name from email."""
        for mail in self.mailbox.fetch(AND(from_=email), limit=1, mark_seen=False):
            name = mail.headers['from'][0]
            name, codec = decode_header(name[:name.index('<')].strip())[0]
            return name.title() if codec is None else name.decode(codec).title()

    def transfer_mail_to_mailbox_and_archive(self, uids, target_mailbox: MailBox, archive_folder, target_folder,
                                             print_info=False):
        """Transfer and archive mail."""
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
            target_mailbox.append(mail, target_folder,
                                  dt=datetime.datetime.strptime(mail.date_str, "%a, %d %b %Y %H:%M:%S %z"))
            uids_to_move.append(mail.uid)
        self.mailbox.move(uids_to_move, archive_folder)

        if print_info and len(uids_to_move) > 0:
            print(f'[{datetime.datetime.now().strftime("%H:%M %d.%m")}] '
                  f'A total of {len(uids_to_move)} letters have been moved.')

    def transfer_mail_to_mailbox_and_mark_seen(self, target_mailbox: MailBox, target_folder, print_info=False):
        """Transfer and mark seen."""
        mails = self.mailbox.fetch(AND(all=True, seen=False), bulk=True, mark_seen=True)

        moved_count = 0
        for mail in mails:
            target_mailbox.append(mail, target_folder,
                                  dt=datetime.datetime.strptime(mail.date_str, "%a, %d %b %Y %H:%M:%S %z"))
            moved_count += 1

        if print_info and moved_count > 0:
            print(f'[{datetime.datetime.now().strftime("%H:%M %d.%m")}] '
                  f'A total of {moved_count} letters have been moved.')
