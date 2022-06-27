"""Email main."""
import argparse

from netjudge.email_helper.fac_idle import fac_idle_main
from netjudge.email_helper.ya_idle import ya_idle_main
from netjudge.email_helper.ya_download import ya_download

arg_parser = argparse.ArgumentParser()

arg_parser.add_argument('--type', type=str, choices=['ya_idle', 'fac_idle', 'ya_download'])

if __name__ == '__main__':
    args = arg_parser.parse_args()
    if args.type == 'ya_idle':
        ya_idle_main()
    elif args.type == 'fac_idle':
        fac_idle_main()
    elif args.type == 'ya_download':
        ya_download(print_info=True)
