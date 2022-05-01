import argparse

from .fac_idle import fac_idle_main
from .ya_idle import ya_idle_main
from .ya_download import ya_download

arg_parser = argparse.ArgumentParser()

arg_parser.add_argument('--type', type=str, choices=['ya_idle', 'fac_idle', 'ya_parse', 'ya_download'])

if __name__ == '__main__':
    args = arg_parser.parse_args()
    if args.type == 'idle_ya':
        ya_idle_main()
    elif args.type == 'idle_fac':
        fac_idle_main()
    elif args.type == 'ya_parse':
        import ya_parse
    elif args.type == 'ya_download':
        ya_download()
