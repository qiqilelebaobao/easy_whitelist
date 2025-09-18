import logging

from .config import arg
from .log.log import set_log
from .tcloud.core import t_main



def main() -> None:

    tencent, alibaba, action, target, target_id, proxy, verbose = arg.init_arg()

    set_log(verbose)

    cloud_provider = 'tencent' if tencent else 'aliyun'
    logging.info('Using %s cloud provider', cloud_provider.upper())

    if cloud_provider == 'tencent':
        t_main(action, target, target_id, proxy)
