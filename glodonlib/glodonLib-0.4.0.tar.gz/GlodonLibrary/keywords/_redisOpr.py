# coding: utf-8

import redis


class RedisFunc:
    """abount redis'function  """

    def GetPictureValue(self, strKey):
        
        redisClient = self.connect_redis()
        strCaptchaKey = '\xAC\xED\x00\x05t\x00\x12RelateCaptchaCache\xAC\xED\x00\x05t\x00 ' + strKey
        strValue = redisClient.get(strCaptchaKey)
        if isinstance(strValue, str):
            strHexValue = "".join("{:02x}".format(ord(c)) for c in strValue).upper()
            strCapchaHexValue = strHexValue.replace('ACED0005740004', '')
            strCapchaValue = bytearray.fromhex(strCapchaHexValue)
            return strCapchaValue

    def GetSmsValue(self, strKey):
        
        redisClient = self.connect_redis()
        strSmsKey = '\xAC\xED\x00\x05t\x00\x0ERelateSmsCache\xAC\xED\x00\x05t\x00\x19smsCode_' + strKey
        strValue = redisClient.get(strSmsKey)
        if isinstance(strValue, str):
            strHexValue = "".join("{:02x}".format(ord(c)) for c in strValue).upper()
            strSmsHexValue = strHexValue.replace('ACED0005740006', '')
            strSmsValue = bytearray.fromhex(strSmsHexValue)
            return strSmsValue
    
    def connect_redis(self,host='10.129.60.111', port=16379, db=0, password='KTiEeI3P4Cz8s4XvksOn'):
        """
        链接redis
        :param host:
        :param port:
        :param db:
        :param password:
        :return:
        """
        redisClient = redis.StrictRedis(host=host, port=port, db=db, password=password)
        return redisClient
    
    def get_redis_value(self, redisObject, key):
        """
        获取redis指定key的值
        :param redisObject:
        :param key:
        :return:
        """
        return redisObject.get(key)
