import requests
import sys
import random
import re

from . import url

def get_local_ip_from_url_and_parse(u, patt, ag):
    # 发送GET请求
    headers = {'user-agent': ag}
    # print(f'user_agent:{ag}')
    try:
        response = requests.get(u, headers=headers, timeout=60)
        # 获取响应内容
        respon = response.text
        l_ip = url.parse_ip_from_response(respon, patt)
        return l_ip
    except Exception:
        return None

def validate_ip(l_ip):
    if not l_ip:
        return False
        
    # r'(?:(?:25[0-5]|2[0-4][0-9]|[1]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[1]?[0-9][0-9]?)'
    # r'(?:\d{1,3}\.){3}\d{1,3}'
    # r'((?:[1-9]?\d|1\d\d|2[0-4]\d|25[0-5])\.){3}(?:[1-9]?\d|1\d\d|2[0-4]\d|25[0-5])'
    # r'(?<![\.\d])(?:25[0-5]\.|2[0-4]\d\.|[01]?\d\d?\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)(?![\.\d])'
    pat = r'((?:[1-9]?\d|1\d\d|2[0-4]\d|25[0-5])\.){3}(?:[1-9]?\d|1\d\d|2[0-4]\d|25[0-5])'
    if re.fullmatch(pat, l_ip):
        return True
    else:
        return False

def get_local_ips():
    ip_list = []
    for i, u in enumerate(url.detect_url, 1):
        l_ip = get_local_ip_from_url_and_parse(u[0], u[1], u[2])
        if validate_ip(l_ip):
            ip_list.append(l_ip)
    return ip_list

def print_ip_list(ip_list):
    number = 100
    print(f'{"Detected Local IP List":=^{number}}\n'
          f'{"#":<38}IP Address\n'
          f'{"-" * number}'
          )
    
    for i, ip in enumerate(ip_list, 1):
        print(f'{str(i):<38}{ip}')

    print('-' * number)


if __name__ == '__main__':
    print(validate_ip('1.0.0.0'))