import os

from tencentcloud.common import credential
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.common_client import CommonClient


def get_common_client(proxy):
    # cred = credential.Credential(
    #     os.environ.get("TENCENTCLOUD_SECRET_ID"),
    #     os.environ.get("TENCENTCLOUD_SECRET_KEY"))
    
    cred = credential.DefaultCredentialProvider().get_credential()

    httpProfile = HttpProfile()
    # httpProfile.endpoint = "vpc.tencentcloudapi.com"
    httpProfile.proxy = f'127.0.0.1:{proxy}' if proxy else None
    
    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile
    # clientProfile.signMethod = 'HmacSHA256'
    
    common_client = CommonClient("vpc", "2017-03-12", cred, "ap-nanjing", profile=clientProfile)
    
    return common_client