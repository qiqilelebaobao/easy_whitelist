import re
import random

from .agent import *
from .pattern import *


def parse_ip_from_response(response, patt):
    if result:=re.search(patt, response):
        return result.group(1)

detect_url = [
    ['https://ifconfig.me', IFCONFIG_ME_PATTERN, random.choice(curl_user_agent)],
    ['http://cip.cc', CIP_CC_PATTERN, random.choice(chrome_user_agent)],
    ['https://tool.lu/ip/', TOOL_LU_PATTERN, random.choice(chrome_user_agent)]
]