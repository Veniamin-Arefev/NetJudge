import argparse

from email_helper.mailer_configs import load_configs
from .fac_idle import fac_idle_main
from .ya_idle import ya_idle_main
from .ya_download import ya_download
from .ya_parse import ya_parse_main
from .table_utilities import create_html_from_database

arg_parser = argparse.ArgumentParser()

arg_parser.add_argument('--type', type=str, choices=['ya_idle', 'fac_idle', 'ya_parse',
                                                     'ya_download', 'ya_parse_database'])

if __name__ == '__main__':
    args = arg_parser.parse_args()
    if args.type == 'ya_idle':
        ya_idle_main()
    elif args.type == 'fac_idle':
        fac_idle_main()
    elif args.type == 'ya_parse':
        ya_parse_main(print_info=True)
    elif args.type == 'ya_download':
        ya_download(print_info=True)
    elif args.type == 'ya_parse_database':
        configs = load_configs('mailer_ya.cfg')
        create_html_from_database(target_path=configs['Output']['Path to directory'],
                                  target_filename=configs['Output']['File name'])
