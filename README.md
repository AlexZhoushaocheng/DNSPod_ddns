# dnspod DDNS ipv6
在群晖上使用ddns不持支ipv6，所以自己做一个python脚本。域名供应商是腾讯的dnspod。

## requirements
* tencentcloud-sdk-python-common==3.0.991
* tencentcloud-sdk-python-dnspod==3.0.991


``` sh
使用国内源安装：

pip install -i https://pypi.tuna.tsinghua.edu.cn/simple tencentcloud-sdk-python-common
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple tencentcloud-sdk-python-dnspod
```
## usage

### conf.ini
```ini
[credential]
secret_id= 
secret_key= 

[domain]
domain=
```

## Run
./ddns.sh