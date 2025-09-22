import json
import random
import sys
import logging

from typing import List, Optional


from ..ip_detector import detectors
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException

# ---------- 常量 ----------
TEMPLATE_PREFIX = "EW-TEMPLATE-"
TEMPLATE_ID_PREFIX = "ipm-"
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
        # templates = common_client.call_json("DescribeAddressTemplates", params, options = {'SkipSign': True})
        return common_client.call_json("DescribeAddressTemplates", {})

    except TencentCloudSDKException as e:
        logging.error("[DescribeAddressTemplates] failed, type [%s]: %s", type(e).__name__, e)
        return None


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
            pass
        else:
            print(
                'This is not a template generated from this tool. Shall not be modified.')
            return False
    except (TencentCloudSDKException, IndexError) as err:
        # IndexError catch when there is no match target.Example: 'AddressTemplateSet': []
        logging.error("[template] api failed, reason=exception, detail=%s", err)
        sys.exit(1)

    params = {"AddressTemplateId": target_id,
              "AddressesExtra": [{"Address": ip, "Description": "client_ip"} for ip in client_ips]
              }

    try:
        respon = common_client.call_json(
            "ModifyAddressTemplateAttribute", params)

    except TencentCloudSDKException as err:
        logging.error("[template] api failed, reason=exception, detail=%s", err)
        return False

    return True


def set_template(common_client, target_id, proxy=None):

    if target_id:
        if target_id.startswith(TEMPLATE_ID_PREFIX):
            client_iplist = _get_iplist(proxy)
            if _modify_template_address(common_client, target_id, client_iplist):
                print(f"✅ [成功] 模板 {target_id} 已更新 -> {client_iplist}")
        else:
            logging.warning("[template] set failed, reason=wrong template id '%s', hint=check prefix", target_id)
    else:
        logging.error("[template] missing template_id, reason=empty input, detail=none")


def create_template_and_associate(common_client, rule_id, proxy=None):

    if not rule_id:
        logging.info('[template] missing security_group_id.')
        return False
    # check rule_id
    pass

    template_id = create_template(common_client, proxy)
    logging.info(f'[template] Get template id {template_id}.')

    if template_id is None:
        logging.info('[template] create failed.')
        return False

    return associate_template_2_rule(common_client, template_id, rule_id)


def create_template(common_client, proxy=None):
    try:
        templates = []
        respon = common_client.call_json("DescribeAddressTemplates", {})
        logging.info(f'[template] api response: {json.dumps(respon, ensure_ascii=False)}')
        for template in respon['Response']['AddressTemplateSet']:
            if template['AddressTemplateName'].startswith(TEMPLATE_PREFIX):
                templates.append(
                    (template['AddressTemplateId'], template['AddressTemplateName'], template['CreatedTime']))
        if templates:
            logging.error(f'[template] already have template without creation: {templates}')
            return templates[0][0]

        ip_list = _get_iplist(proxy)
        random_suffix = random.randint(1, 9999)
        params = {
            "AddressTemplateName": f"{TEMPLATE_PREFIX}{random_suffix:04d}",
            "AddressesExtra": [{"Address": ip, "Description": "client_ip"} for ip in ip_list]
        }
        respon = common_client.call_json("CreateAddressTemplate", params)

        logging.info(f'[template] api response: {json.dumps(respon, ensure_ascii=False)}')

    except TencentCloudSDKException as err:
        logging.error("[template] api failed, reason=exception, detail=%s", err)
        return None

    return respon['Response']['AddressTemplate']['AddressTemplateId']


def associate_template_2_rule(common_client, template_id, rule_id):
    try:
        params = {"SecurityGroupId": f'{rule_id}',
                  "SecurityGroupPolicySet":
                      {"Ingress": [
                          {"PolicyIndex": 0, "Protocol": "ALL", "AddressTemplate": {
                              "AddressId": f'{template_id}'},
                           "Action": "ACCEPT", "PolicyDescription": "Easy Whitelist"}
                      ]}
                  }

        respon = common_client.call_json(
            "CreateSecurityGroupPolicies", params
        )
        logging.info(f'[template] api response: {json.dumps(respon, ensure_ascii=False)}')

    except TencentCloudSDKException as err:
        logging.error("[template] api failed, reason=exception, detail=%s", err)
        return False

    return True
