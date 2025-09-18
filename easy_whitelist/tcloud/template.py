import json
import random
import sys
import logging

from typing import List, Optional


from ..ip_detector import detectors
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException

# ---------- 常量 ----------
TEMPLATE_PREFIX = "temp-open-"
HEADER_WIDTH = 150
COLS = {
    "idx": 10,
    "id": 20,
    "ctime": 30,
    "addrs": 60,
    "name": 30,
}

# 这段是获取和打印模版


def _get_template(common_client) -> Optional[dict]:
    try:
        params = {}
        # templates = common_client.call_json("DescribeAddressTemplates", params, options = {'SkipSign': True})
        return common_client.call_json("DescribeAddressTemplates", params, )

    except TencentCloudSDKException as e:
        logging.error("DescribeAddressTemplates failed: %s", e)
        return None


def _write_template_list_to_temp_file(template_ids):

    with open('/tmp/template_0000.txt', 'w') as temp_file:
        json.dump(template_ids, temp_file)

    return temp_file.name


def print_template(common_client) -> List[str]:

    if not (tpl_resp := _get_template(common_client)):
        return []

    template_ids = []

    # 表头
    header = (f'{"#":<{COLS["idx"]}}'
              f'{"Template ID":<{COLS["id"]}}'
              f'{"CreatedTime":<{COLS["ctime"]}}'
              f'{"Addresses":<{COLS["addrs"]}}'
              f'{"AddressTemplateName":<{COLS["name"]}}')

    print(f'{"Tencent Cloud Template List":=^{HEADER_WIDTH}}')
    print(header)
    print("-" * HEADER_WIDTH)

    for i, template in enumerate(tpl_resp['Response']['AddressTemplateSet'], 1):
        template_ids.append(template['AddressTemplateId'])
        # print(template_ids)
        addreset = ', '.join(template['AddressSet'][:3])
        if len(template['AddressSet']) > 3:
            addreset += f' ~~~ {len(template["AddressSet"])-3} more...'
        print(f"{str(i):{COLS["idx"]}}"
              f"{template['AddressTemplateId']:{COLS["id"]}}"
              f"{template['CreatedTime']:{COLS["ctime"]}}"
              f"{addreset:<{COLS["addrs"]}}"
              f"{template['AddressTemplateName']:{COLS["name"]}}"
              )
    print('-' * HEADER_WIDTH)

    # _write_template_list_to_temp_file(template_ids)

    return template_ids


def _get_iplist(proxy=None):
    client_ip_list = detectors.get_local_ips(proxy)
    client_ip_list = list(set(client_ip_list))

    return client_ip_list


def _modify_template_address(common_client, target_id, client_ips):

    if not target_id:
        return False

    # 增加描述校验，避免更改错误
    params = {"Filters": [
        {"Name": "address-template-id", "Values": [target_id]}]}
    try:
        respon = common_client.call_json("DescribeAddressTemplates", params)
        if (TemplateSet := respon['Response']['AddressTemplateSet']) and \
                TemplateSet[0]['AddressTemplateName'].startswith(TEMPLATE_PREFIX):
            # print(respon)
            pass
        else:
            print(
                'This is not a template generated from this tool. Shall not be modified.')
            return False
    except (TencentCloudSDKException, IndexError) as err:
        # IndexError catch when there is no match target.Example: 'AddressTemplateSet': []
        print(f"{err=}, {type(err)=}")
        sys.exit(1)

    params = {"AddressTemplateId": target_id,
              "AddressesExtra": [{"Address": ip, "Description": "client_ip"} for ip in client_ips]
              }

    try:
        respon = common_client.call_json(
            "ModifyAddressTemplateAttribute", params)

    except TencentCloudSDKException as err:
        print(f"Unexpected {err=}, {type(err)=}")
        return False

    return True


def set_template(common_client, target_id, proxy=None):
    # with open('/tmp/template_0000.txt', 'r') as temp_file:
    #     data = json.load(temp_file)
    #     print(data)
    if target_id:
        if target_id.startswith('ipm-'):
            client_iplist = _get_iplist(proxy)
            if _modify_template_address(common_client, target_id, client_iplist):
                print(f"✅ [成功] 模板 {target_id} 已更新 -> {client_iplist}")
        else:
            logging.warning('Wrong template id.')
    else:
        logging.error('Set template shall input template id.')


def create_template(common_client, rule_id, proxy=None):

    if not rule_id:
        print('Create template shall input security group id.')
        return False

    try:
        templates = []
        respon = common_client.call_json("DescribeAddressTemplates", {})
        logging.info(json.dumps(respon, ensure_ascii=False))
        for template in respon['Response']['AddressTemplateSet']:
            if template['AddressTemplateName'].startswith(TEMPLATE_PREFIX):
                templates.append(
                    (template['AddressTemplateId'], template['AddressTemplateName'], template['CreatedTime']))
        if templates:
            print(f'Already have template without creation: {templates}')
            return True

    except TencentCloudSDKException as err:
        print(f"{err=}, {type(err)=}")
        return False

    ip_list = _get_iplist(proxy)
    random_suffix = random.randint(1, 9999)
    params = {
        "AddressTemplateName": f"{TEMPLATE_PREFIX}{random_suffix:04d}",
        "AddressesExtra": [{"Address": ip, "Description": "client_ip"} for ip in ip_list]
    }

    try:
        respon = common_client.call_json(
            "CreateAddressTemplate", params
        )
        print(json.dumps(respon, ensure_ascii=False))

        if template_id := respon['Response']['AddressTemplate']['AddressTemplateId']:

            params = {"SecurityGroupId": f'{rule_id}',
                      "SecurityGroupPolicySet": {"Ingress": [{"PolicyIndex": 0, "Protocol": "ALL", "AddressTemplate": {"AddressId": f'{template_id}'}, "Action": "ACCEPT", "PolicyDescription": "easy-whitelist"}]}
                      }

            respon = common_client.call_json(
                "CreateSecurityGroupPolicies", params
            )
            print(json.dumps(respon))

    except TencentCloudSDKException as err:
        print(f"{err=}, {type(err)=}")
        return False

    return True
