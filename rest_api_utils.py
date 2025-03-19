import json
import re

import requests
from requests.auth import HTTPBasicAuth

def call_rest_api(method, url, auth=None, data=None, headers=None, params=None):
    """
    通用 REST API 调用方法
    :param method: 请求方法 ("GET", "POST", "PUT", "DELETE")
    :param url: API 地址
    :param auth: 认证信息 (可选, 例如 BasicAuth 或 Bearer Token)
    :param data: 发送的数据 (POST/PUT 请求)
    :param headers: 自定义请求头 (可选)
    :param params: URL 查询参数 (可选)
    :return: 响应 JSON 数据或错误信息
    """
    errinfo = ""
    try:
        fixed_url = re.sub(r'(?<!:)//+', '/', url)
        print("url: {},data:{},headers:{},params:{}".format(fixed_url, data, headers, params))

        response = requests.request(
            method=method.upper(),
            url=fixed_url,
            auth=auth,
            json=data,
            headers=headers,
            params=params
        )
        response.encoding = 'utf-8'
        print(response.text)
        errinfo = response.text
        response.raise_for_status()  # 抛出 HTTP 错误（如 404、500）
        return response.json()  # 返回 JSON 响应
    except requests.exceptions.RequestException as e:
        # if response.status_code == 400:
        #     return json.loads(errinfo)
        raise Exception(errinfo)

