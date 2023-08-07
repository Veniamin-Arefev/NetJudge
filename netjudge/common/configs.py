"""Creating mail configs."""

import configparser
import os.path

from functools import cache

__all__ = ["load_configs"]

default_config_file_name = "mailer.cfg"


def create_default_configs_file():
    """Create default configs."""
    config = configparser.ConfigParser()
    config["Logging"] = {
        "console level": "INFO",
        "file level": "DEBUG",
    }
    config["Fac Credentials"] = {
        "username": "user",
        "password": "password",
    }
    config["Yandex Credentials"] = {
        "Username": "User",
        "Password": "Password",
    }
    config["Fac Server"] = {
        "timeout time": "600",
        "email server host": "imap.cs.msu.ru",
        "folder": "INBOX",
        "storage folder": "LinuxNetwork20XX",
    }
    config["Yandex Server"] = {
        "timeout time": "600",
        "email server host": "imap.yandex.ru",
        "folder": "LinuxNetwork20XX",
    }
    config["Web server"] = {
        "hostname": "localhost",
        "port": "8080",
        "super secret cookie": "LinuxNetwork20XX",
        "course name": "LinuxNetwork20XX",
    }
    config["Homework names"] = {
        "1": "01_HardwareAndCommandline",
        "2": "02_DataLink",
        "3": "03_BridgeVlan",
    }
    config["Homework files"] = {
        "1": ["report.01.base", "report.01.clone"],
        "2": ["report.02.base", "report.02.clone"],
        "3": ["report.03.base", "report.03.clone", "report.03.bridge"],
    }
    config["Homework deadlines"] = {
        "1": "2022-02-23",
        "2": "2022-03-02",
        "3": "2022-03-09",
    }
    config["Rating grades"] = {
        "on_time": "4",
        "week": "2",
        "fortnight": "1",
        "bad_archive": "0",
        "plagiarism": "0",
    }

    with open(default_config_file_name, "w") as configfile:
        config.write(configfile)


@cache
def load_configs(
    config_file_name: str = default_config_file_name,
) -> configparser.ConfigParser:
    """Load configs."""
    if os.path.isfile(config_file_name):
        config = configparser.ConfigParser()
        with open(config_file_name, "r") as configfile:
            config.read_file(configfile)
            return config
    else:
        create_default_configs_file()
        raise FileNotFoundError(
            "Config file doesnt exist. We created default file. Please fill it with your data."
        )
