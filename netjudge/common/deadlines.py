"""Task deadlines and names."""
from datetime import datetime, timedelta
from ast import literal_eval
from netjudge.common.configs import load_configs

__all__ = ['homeworks_names_and_files', 'deadlines']

configs = load_configs()
homeworks_names_and_files = dict(
    zip([*configs['Homework names'].values()], map(lambda x: literal_eval(x), [*configs['Homework files'].values()])))


def get_deadlines(keys: list, date: list):
    """Get task deadline."""
    deadlines_format = '%Y-%m-%d %z'
    return_dict = {}
    for index, key in enumerate(keys):
        return_dict[key] = datetime.strptime(date[index] + ' +0300', deadlines_format) + timedelta(days=1)
    return return_dict


# noinspection PyTypeChecker
deadlines = get_deadlines(homeworks_names_and_files.keys(), [*configs['Homework deadlines'].values()])
