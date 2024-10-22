import os

from tencentcloud.common import credential
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.common_client import CommonClient


def get_common_client(proxy):
    cred = credential.Credential(
        os.environ.get("TENCENTCLOUD_SECRET_ID"),
        os.environ.get("TENCENTCLOUD_SECRET_KEY"))

    httpProfile = HttpProfile()
    httpProfile.endpoint = "vpc.tencentcloudapi.com"
    if proxy != -1:
        httpProfile.proxy = f'127.0.0.1:{proxy}'
    
    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile
    
    common_client = CommonClient("vpc", "2017-03-12", cred, "ap-nanjing", profile=clientProfile)
    
    return common_client