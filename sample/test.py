# -*- coding: utf-8 -*-
import json
import os

from tencentcloud.common.common_client import CommonClient
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile

try:
    cred = credential.Credential(
        os.environ.get("TENCENTCLOUD_SECRET_ID"),
        os.environ.get("TENCENTCLOUD_SECRET_KEY"))

    pass

    httpProfile = HttpProfile()
    httpProfile.endpoint = "vpc.tencentcloudapi.com"
    httpProfile.proxy = '127.0.0.1:8080'
    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile

    headers = {}
    common_client = CommonClient("vpc", "2017-03-12", cred, "ap-nanjing", profile=clientProfile)
    templates = common_client.call_json("DescribeAddressTemplates", headers)
    print(json.dumps(templates, ensure_ascii=False))

except TencentCloudSDKException as err:
    print(err)