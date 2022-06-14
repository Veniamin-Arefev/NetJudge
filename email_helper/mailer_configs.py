"""Creating mail configs."""

import configparser
import os.path

__all__ = ['load_configs']

default_config_file_name = 'mailer.cfg'


def create_default_configs_file():
    """Create default configs."""
    config = configparser.ConfigParser()
    config['Credentials'] = {
        'Username': 'User',
        'Password': 'Password',
    }
    config['Server'] = {
        'email server host': 'imap.yandex.ru',
        'folder': 'INBOX',
    }
    config['Checker'] = {
        'Sliding window days': '0',
        'Sliding window hours': '0',
        'Sliding window minutes': '0',
    }
    config['Output'] = {
        'Path to directory': '0',
        'File name': '0',
    }
    with open(default_config_file_name, 'w') as configfile:
        config.write(configfile)


def load_configs(config_file_name: str = default_config_file_name) -> configparser.ConfigParser:
    """Load configs."""
    if os.path.isfile(config_file_name):
        config = configparser.ConfigParser()
        with open(config_file_name, 'r') as configfile:
            config.read_file(configfile)
            return config
    else:
        create_default_configs_file()
        raise FileNotFoundError('Config file doesnt exist. We created default file. Please fill it with your data.')
