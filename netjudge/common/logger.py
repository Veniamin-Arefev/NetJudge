"""Logging infrastructure"""
import logging
import sys
from pathlib import Path
from typing import Optional

from netjudge.common.configs import load_configs


def set_up_logger(logger: logging.Logger, true_name: str):
    """Set up logger for first time"""
    configs = load_configs()

    logger.setLevel(logging.DEBUG)

    Path("./logs").mkdir(exist_ok=True)
    file_handler = logging.FileHandler(f"./logs/{true_name}.log")
    file_handler.setLevel(configs['Logging']['file level'])

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(configs['Logging']['console level'])

    formatter = logging.Formatter(fmt="{asctime} |{name:>12}|: {levelname:>7} {message}", datefmt="%H:%M:%S %d.%m.%Y", style="{")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def get_logger(package_name: str, true_name: Optional[str] = None):
    """Get logger for current package"""
    if true_name is None:
        true_name = package_name.split(".")[1]

    root_logger = logging.getLogger()

    if not root_logger.hasHandlers():
        set_up_logger(root_logger, true_name)

    return logging.getLogger(true_name)
