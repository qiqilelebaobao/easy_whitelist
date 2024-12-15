import json
import random
import sys
import logging

from ..ip import ip
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException


def write_template_list_to_temp_file(template_ids):

    with open('/tmp/template_0000.txt', 'w') as temp_file:
          json.dump(template_ids, temp_file)
    
    return temp_file.name

def get_template(common_client):
    try:
        params = {}
        # templates = common_client.call_json("DescribeAddressTemplates", params, options = {'SkipSign': True})
        templates = common_client.call_json("DescribeAddressTemplates", params, )
        return templates

    except TencentCloudSDKException as err:
        print(err)
        return None

def list_template(common_client):
    number = 150
    print(f'{"Tencent Cloud Template List":=^{number}}\n' \
          f'{"#":<10}{"Template ID":<20}{"CreatedTime":<30}{"Addresses":<60}{"AddressTemplateName":<30}\n' \
          f'{"-" * number}'
          )

    template_ids = []
    if not(templates := get_template(common_client)):
        return template_ids

    for i, template in enumerate(templates['Response']['AddressTemplateSet'], 1):
        template_ids.append(template['AddressTemplateId'])
        # print(template_ids)
        addreset = ' ~ '.join(template['AddressSet'][:3])
        if len(template['AddressSet']) > 3:
            addreset += f' ~~~ {len(template["AddressSet"])-3} more...'
        print(f"{str(i):10}"
              f"{template['AddressTemplateId']:20}"
              f"{template['CreatedTime']:30}"
              f"{addreset:<60}"
              f"{template['AddressTemplateName']:30}"
              )
    print('-' * number)
    
    # write_template_list_to_temp_file(template_ids)
    
    return template_ids

def format_addres_extra_string_from_list(client_ips):
    cs = '"AddressesExtra":['
    for client_ip in client_ips:
        cs += '{{"Address":"{}","Description":"client_ip"}},'.format(client_ip)
    cs_format = cs.rstrip(',')
    cs_format += ']'
    
    return cs_format

def modify_template_address(common_client, client_ips, target_id):
    
    if not target_id:
        return False
    
    # 增加描述校验，避免更改错误
    params = f"{{\"Filters\":[{{\"Name\":\"address-template-id\",\"Values\":[\"{target_id}\"]}}]}}"
    try:
        respon = common_client.call_json("DescribeAddressTemplates", json.loads(params))
        if (TemplateSet := respon['Response']['AddressTemplateSet']) and \
            TemplateSet[0]['AddressTemplateName'].startswith('temp-open-'):
            # print(respon)
            pass
        else:
            print('This is not a template generated from this tool. Shall not be modified.')
            return False
    except (TencentCloudSDKException, IndexError) as err:
        # IndexError catch when there is no match target.Example: 'AddressTemplateSet': []
        print(f"{err=}, {type(err)=}")
        sys.exit(1)

    params = "{{\"AddressTemplateId\":\"{}\",{}}}".format(target_id, client_ips)
    try:
        respon = common_client.call_json("ModifyAddressTemplateAttribute", json.loads(params))
        # print(respon)
        # print('-' * 100)
    except TencentCloudSDKException as err:
        print(f"Unexpected {err=}, {type(err)=}")
        return False

    return True

def get_local_ip_and_format_addressesextra(proxy=None):
        client_ip_list = ip.get_local_ips(proxy)
        # ip.print_ip_list(client_ip_list)
        client_ip_list = list(set(client_ip_list))
        addresses_extra = format_addres_extra_string_from_list(client_ip_list)

        return addresses_extra
    
def set_template(common_client, target_id, proxy=None):
    # with open('/tmp/template_0000.txt', 'r') as temp_file:
    #     data = json.load(temp_file)
    #     print(data)
    if target_id:
        if target_id.startswith('ipm-'):
            addresses_extra = get_local_ip_and_format_addressesextra(proxy)
            if modify_template_address(common_client, addresses_extra, target_id):
                logging.info(f'Successfully set {{{target_id}}} to {{{addresses_extra}}}')
        else:
            logging.warning('Wrong template id.')
    else:
        logging.error('Set template shall input template id.')

def create_template(common_client, rule_id, proxy=None):
    
    if not rule_id:
        print('Create template shall input security group id.')
        return False
    
    params = "{}"
    try:
        templates = []
        respon = common_client.call_json("DescribeAddressTemplates", json.loads(params))
        print(json.dumps(respon, ensure_ascii=False))
        for template in respon['Response']['AddressTemplateSet']:
            if template['AddressTemplateName'].startswith('temp-open-'):
                templates.append((template['AddressTemplateId'], template['AddressTemplateName'], template['CreatedTime']))
        if templates:
            print(f'Already have template without creation: {templates}')
            return True

    except TencentCloudSDKException as err:
        print(f"{err=}, {type(err)=}")
        return False

    addresses_extra = get_local_ip_and_format_addressesextra(proxy)
    params = f"{{\"AddressTemplateName\":\"temp-open-{random.randint(1,9999):04d}\",{addresses_extra}}}"
    try:
        respon = common_client.call_json("CreateAddressTemplate", json.loads(params))
        print(json.dumps(respon, ensure_ascii=False))
        
        if template_id := respon['Response']['AddressTemplate']['AddressTemplateId']:
            params = f"{{\"SecurityGroupId\":\"{rule_id}\",\"SecurityGroupPolicySet\":{{\"Ingress\":[{{\"PolicyIndex\":0,\"Protocol\":\"ALL\",\"AddressTemplate\":{{\"AddressId\":\"{template_id}\"}},\"Action\":\"accept\",\"PolicyDescription\":\"temp-open\"}}]}}}}"
            respon = common_client.call_json("CreateSecurityGroupPolicies", json.loads(params))
            print(json.dumps(respon))

    except TencentCloudSDKException as err:
        print(f"{err=}, {type(err)=}")
        return False

    return True
