import os

from tencentcloud.common import credential
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.common_client import CommonClient


def get_common_client(proxy_port):
    # cred = credential.Credential(
    #     os.environ.get("TENCENTCLOUD_SECRET_ID"),
    #     os.environ.get("TENCENTCLOUD_SECRET_KEY"))
    
    cred = credential.DefaultCredentialProvider().get_credential()

    httpProfile = HttpProfile()
    httpProfile.endpoint = "vpc.tencentcloudapi.com"
    httpProfile.proxy = f'127.0.0.1:{proxy_port}' if proxy_port else None
    
    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile
    # clientProfile.signMethod = 'HmacSHA256'
    
    common_client = CommonClient("vpc", "2017-03-12", cred, "ap-guangzhou", profile=clientProfile)
    
    return common_client