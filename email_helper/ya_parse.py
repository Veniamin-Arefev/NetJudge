"""Yandex parser."""
from email_helper.mailer_configs import load_configs
from email_helper.table_utilities import create_html_from_database

__all__ = ['ya_parse_main']


def ya_parse_main():
    """Parser function."""
    configs = load_configs('mailer_ya.cfg')

    create_html_from_database(target_path=configs['Output']['Path to directory'],
                              target_filename=configs['Output']['File name'])
