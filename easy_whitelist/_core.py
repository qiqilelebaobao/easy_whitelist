import logging

from .config import arg
from .config.log import set_log
from .tcloud.core import t_main


def main() -> None:

    # tencent, alibaba, action, target, target_id, proxy, verbose = arg.init_arg()
    args = arg.init_arg()

    set_log(args.verbose)
    logging.info(f'Arg info:{args}')

    cloud_provider = args.cloud
    logging.info('Using %s cloud provider', cloud_provider.upper())

    if cloud_provider == 'tencent':
        t_main(args.action, args.target, args.target_id,args.proxy)
