# coding:utf-8
import time
import jwt, datetime
import json
import base64


# from werkzeug.exceptions import BadRequest

def generate_access_token(client_id, client_secret, username, exp=86400, **kwargs):
    exp = time.time() + exp
    payload = {
        'exp': exp,
        'iat': time.time(),
        'iss': client_id,
        'sub': username,
        'aud': 'smartracing.cn',
    }
    if kwargs is not None:
        payload.update(kwargs)

    access_token = jwt.encode(payload, client_secret, algorithm='HS256', headers={'kid': str(client_id)})
    return {
        'token_type': 'Bearer',
        'access_token': str(access_token, 'utf-8'),
        'expires_in': exp
    }


def read_token(token, client_secret):
    """
    从Json Web Token中将 client_id, username, pid, bid, uid 读出
    :param req:
    :return:
    """
    header = jwt.get_unverified_header(token)
    # 不验证签名就解开claims
    claims = jwt.decode(token,
                        key=client_secret,
                        options={'verify_aud': False})
    return {
        'client_id': header.get('kid'),
        'username': claims.get('sub'),
        'pid': claims.get('pid'),
        'bid': claims.get('bid'),
        'uid': claims.get('uid'),
        'mid': claims.get('mid')
    }


def decode_token(token):
    '''
    直接解包jwt，而不做client_secret验证
    '''
    data = json.loads(
        str(base64.urlsafe_b64decode(
            token.split(".")[1] + '=' * (4 - len(token.split(".")[1]) % 4)
        ), "utf-8")
    )
    return {
        'username': data.get('sub'),
        'pid': data.get('pid'),
        'bid': data.get('bid'),
        'uid': data.get('uid'),
        'mid': data.get('mid')
    }
