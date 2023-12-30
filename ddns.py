import logging
import logging.handlers 

import json
import subprocess

from config import ConfigMrg

from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.dnspod.v20210323 import dnspod_client, models

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"


# 开启文件日志
def setup_log():
    logging.basicConfig(format=LOG_FORMAT)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    file_handler = logging.handlers.RotatingFileHandler('log.txt', backupCount=0, maxBytes=2048)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(file_handler)
    


# 获取主记录id, value
def getRecordId(client:dnspod_client.DnspodClient):
    try:
        req = models.DescribeRecordListRequest()
        params = {
            "Domain": "{}".format(ConfigMrg().get_domain())
        }
        req.from_json_string(json.dumps(params))
        res = client.DescribeRecordList(req)
        j_ret = res._serialize()
        # print(j_ret)
        for rec in j_ret['RecordList']:
            if rec['Name'] == '@' and rec['Type'] == 'AAAA' and rec['Line'] == '默认':
                return rec['RecordId'], rec['Value']
        
        return None
    except TencentCloudSDKException as err:
        logging.exception(err)
    except Exception as ex:
        logging.exception(err)


# 获取ipv6地址
def getIpv6()->str:
    cmd = subprocess.Popen("ip -f inet6  address | sed -n '/\/64.*dynamic/p' | awk '{print $2}' | sed 's#/.*##'", stdout=subprocess.PIPE, shell = True)
    cmd.wait(2)
    return cmd.stdout.read().decode().strip()

try:
    # 开启日志
    setup_log()
    logging.info('---------------------------update start-------------------------------')


    cred = credential.Credential(ConfigMrg().get_secret_id(), ConfigMrg().get_secret_key())
    httpProfile = HttpProfile()
    httpProfile.endpoint = "dnspod.tencentcloudapi.com"

    # 实例化一个client选项，可选的，没有特殊需求可以跳过
    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile
    # 实例化要请求产品的client对象,clientProfile是可选的
    client = dnspod_client.DnspodClient(cred, "", clientProfile)

    [record_id, current_ip_value] = getRecordId(client)
    
    logging.info("record_id:{} current_ip_value:{}".format(record_id, current_ip_value))
    
    addr_ipv6 = getIpv6()
    logging.info("local ipv6:{}".format(addr_ipv6))
    if addr_ipv6 == "":
        logging.error("ipv6 is empty, ensure your ipv6 network is okay")
        logging.info('---------------------------update failed-------------------------------')
        exit(-1)
    # 当前记录中的值和本地的ip相同则不用更新
    if current_ip_value == addr_ipv6:
        logging.info("current record value is already same as local ip, no need update")
    else:
        # 实例化一个请求对象,每个接口都会对应一个request对象
        req = models.ModifyRecordRequest()
        params = {
            "Domain": "{}".format(ConfigMrg().get_domain()),
            "RecordType": "AAAA",
            "RecordLine": "默认",
            "Value": addr_ipv6,
            "RecordId": record_id
        }
        req.from_json_string(json.dumps(params))

        # 返回的resp是一个ModifyRecordResponse的实例，与请求对象对应
        resp = client.ModifyRecord(req)
        
        # 输出json格式的字符串回包
        logging.info(resp.to_json_string())
    
    logging.info('---------------------------update done-------------------------------')

except TencentCloudSDKException as err:
    logging.exception(err)
except Exception as ex:
    logging.exception(ex)