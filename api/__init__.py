import hashlib
import configparser
from flask import request, jsonify
import os

config = configparser.ConfigParser()
path = os.path.abspath(os.path.dirname(os.path.dirname(__file__))) + "/config.ini"
config.read(path)


def signature(params: dict):
    """
    根据请求进行签名
    :param params: 请求参数
    :return:
    """
    commons = ['timestamp', 'nonce', 'appkey', 'sign', 'token']
    m = hashlib.md5()
    lst = [f"{k}={v}" for k, v in params.items() if k not in commons]
    lst.sort()
    msg = '&'.join(lst)
    token = params.get('token', '')
    timestamp = params.get('timestamp', '')
    nonce = params.get('nonce')
    appkey = params.get('appkey', '')

    m.update(f'{msg}{token}{timestamp}{nonce}{_get_app_secret(appkey)}'.encode('utf-8'))
    return m.hexdigest()


def _get_app_secret(appkey: str):
    key = config['APP']['appkey']
    if appkey == key:
        return config['APP']['appsecret']
    return ''


def validsign(func):
    """
    验证签名
    :param func:
    :return:
    """

    def decorator():
        params = request.form
        appkey = params.get('appkey')
        sign = params.get('sign')
        csign = signature(params)
        if not appkey:
            return make_response_error(300, 'appkey is none.')
        if csign != sign:
            return make_response_error(500, 'signature is error.')
        return func()

    return decorator


def make_response_ok(data=None):
    """
    请求成功返回的结果
    :param data:
    :return:
    """
    resp = {'code': 0, 'msg': 'success'}
    if data:
        resp['data'] = data
    return jsonify(resp)


def make_response_error(code, msg):
    """
    请求失败返回的结果
    :param code:
    :param msg:
    :return:
    """
    resp = {'code': code, 'msg': msg}
    return jsonify(resp)
