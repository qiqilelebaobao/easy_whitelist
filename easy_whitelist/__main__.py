#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys

import json
import os
import pprint
import string

from easy_whitelist.config import arg
from easy_whitelist.tcloud import client
from easy_whitelist.tcloud.template import list_template, set_template, create_template


LOG_FORMAT = '%(asctime)s-%(process)d-%(filename)s:%(lineno)d-%(levelname)s-%(message)s'
INPUT_PROMPT = 'Please choose # template to set (or [L]ist, [C]reate, [Q]uit): '

def loop_list(common_client, proxy=None):
    template_ids = list_template(common_client)
    last_input = None

    while True:

        try:
            user_input = input(INPUT_PROMPT).strip().lower()

            if user_input == 'q':
                break

            if last_input == '' and user_input == '':
                break

            last_input = user_input

            if user_input == '':
                continue

            if user_input == 'l':
                list_template(common_client)
                continue

            if user_input.isdigit():
                if template_ids:
                    if (a := int(user_input)) > 0 and a <= len(template_ids):
                        set_template(common_client, template_ids[a - 1], proxy)
                    else:
                        logging.warning(
                            'Index out of range. Available templates: %d', len(template_ids))
                    continue

            logging.warning('Invalid input: %s', user_input)

        except KeyboardInterrupt:
            logging.warning('\nOperation cancelled by user')
            break
        except Exception as e:
            logging.warning("\nUnexpected error occurred: %s", e)


def set_log(verbose: int = 0):

    level_map = {
        0: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG
    }

    level = level_map.get(verbose, logging.WARNING)

    logging.basicConfig(level=level, format=LOG_FORMAT)


def main() -> None:
    tencent, alibaba, action, target, target_id, proxy, verbose = arg.init_arg()

    set_log(verbose)

    common_client = client.get_common_client(proxy)

    cloud_provider = 'tencent' if tencent else 'aliyun'
    logging.info('Using %s cloud provider', cloud_provider.upper())

    if cloud_provider == 'tencent' and target == 'template':
        if action == 'list':
            loop_list(common_client, proxy)
        elif action == 'set':
            set_template(common_client, target_id, proxy)
        elif action == 'create':
            create_template(common_client, target_id, proxy)
        else:
            logging.error('Unsupported operation: %s', action)


if __name__ == '__main__':
    main()
