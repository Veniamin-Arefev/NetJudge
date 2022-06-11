from datetime import datetime, timedelta

__all__ = ['homeworks_names_and_files', 'deadlines']

homeworks_names_and_files = {
    '01_HardwareAndCommandline': ['report.01.base', 'report.01.clone'],
    '02_DataLink': ['report.02.base', 'report.02.clone'],
    '03_BridgeVlan': ['report.03.base', 'report.03.clone', 'report.03.bridge'],
    '04_AddressAndRoute': ['report.04.base', 'report.04.clone', 'report.04.router1', 'report.04.router2'],
    '05_IProuteRule': ['report.05.router', 'report.05.client1', 'report.05.client2'],
    '06_TransportProtocols': ['report.06.client1', 'report.06.client2', 'report.06.client3'],
    '07_TransportNAT': ['report.07.router', 'report.07.srv', 'report.07.clienta', 'report.07.clientb'],
    '08_ApplicationSystem': ['report.08.srv', 'report.08.client'],
    '09_ApplicationSupplemental': ['report.09.srv', 'report.09.client', 'report.09.stranger'],
    '10_FireWalls': ['report.10.server', 'report.10.router', 'report.10.client'],
}


def get_deadlines(keys: list, date: list):
    deadlines_format = '%Y-%m-%d %z'
    return_dict = {}
    for index, key in enumerate(keys):
        return_dict[key] = datetime.strptime(date[index] + ' +0300', deadlines_format) + timedelta(days=1)
    return return_dict


# noinspection PyTypeChecker
deadlines = get_deadlines(homeworks_names_and_files.keys(), [
    '2022-02-23',
    '2022-03-02',
    '2022-03-09',
    '2022-03-18',
    '2022-03-24',
    '2022-04-02',
    '2022-04-09',
    '2022-04-16',
    '2022-04-25',
    '2022-05-02',
])
