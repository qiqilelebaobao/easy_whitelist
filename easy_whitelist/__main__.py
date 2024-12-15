#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import pprint
import string
import sys
import logging

from easy_whitelist.config import arg
from easy_whitelist.tcloud import client
from easy_whitelist.tcloud.template import list_template, set_template, create_template


def loop_list(common_client, proxy=None):
    template_ids = list_template(common_client)
    last_input = None
    while True:
        input_from_user = input('Please choose # template to set (or [L]ist or [Q]uit): ')
        if last_input == '' and input_from_user == '':
            break
        last_input = input_from_user
        if input_from_user.isdigit():
            if template_ids:
                if (a := int(input_from_user)) > 0 and a <= len(template_ids):
                    set_template(common_client, template_ids[a - 1], proxy)
                else:
                    logging.info('Wrong index, please input right index from the list.')
        elif input_from_user == 'l' or input_from_user == 'L':
            list_template(common_client)
        elif input_from_user == 'q' or input_from_user == 'Q':
            break
        elif input_from_user == '':
            continue
        else:
            logging.info('Input error.')

def set_log(verbose=0):
    # FMT = '%(asctime)s %(process)d %(filename)s L%(lineno)s %(levelname)s %(message)s'
    FMT = '%(asctime)s - %(process)d - %(filename)s - L%(lineno)s - %(levelname)s - %(message)s'
    
    if verbose == 0:
        logging.basicConfig(level=logging.WARN, format=FMT)
    elif verbose == 1:
        logging.basicConfig(level=logging.INFO, format=FMT)
    elif verbose >=2:
        logging.basicConfig(level=logging.DEBUG, format=FMT)
    else:
        print("Wrong position in set_log.")
        
def main():
    tencent, alibaba, action, target, target_id, proxy, verbose = arg.init_arg()

    set_log(verbose)

    common_client = client.get_common_client(proxy)
    
    if tencent and target == 'template':
        if action == 'list':
            loop_list(common_client)
        elif action == 'set':
            set_template(common_client, target_id, proxy)
        elif action == 'create':
            create_template(common_client, target_id, proxy)
        else:
            logging.error('Wrong postion, shall not be here.')


if __name__ == '__main__':
    main()
