#!usr/bin/env python
# coding=utf-8
from robot.api import logger
from robot.api.deco import keyword
import hashlib
import time
import json
import hashlib
import random
import pymysql
import jwt
from datetime import datetime,timedelta
from .version import VERSION


__author__ = 'bryan hou'
__email__ = 'bryanhou@gmail.com'
__version__ = VERSION

class PublicLibrary(object):


    

    def __int__(self):
        pass


    @keyword('Generate BUser Token')
    def generate_bUser_token(self, code):
        """
        获取B端用户token

        ``code`` B端用户code

        eg:
        | ${token} | Generate BUser Token | ${bUser_code} |

        """
        SECRET_KEY = "83717cf6a2ba11e8be7c787b8ad1ae43"

        utc_timestamp = datetime.now().timestamp()
        token = jwt.encode({"code": code, "time": utc_timestamp}, SECRET_KEY).decode()
        # utc_timestamp = datetime.now().timestamp()
        # key = "support:jwt:{}".format(code)
        # ex = 60000
        # data = {"exp_time": utc_timestamp + ex, "token": token}
        # redis.set(key, value=json.dumps(data), ex=ex)
        return token

        
    @keyword('Generate CUser Token')
    def generate_cUser_token(self, phone,password,uin):
        """
        获取C端用户token

        ``phone`` c端用户手机号
        ``password`` C端用户密码
        ``uin`` C端用户uin

        eg:
        | ${token} | Generate CUser Token | ${phone} | ${password} | ${uin} |

        """
        token = jwt.encode({"phone": phone, "pwd": password,
                            "exp": int((datetime.now() + timedelta(days=7)).timestamp()), "uin": uin},
                           key="",
                           ).decode()
        return token



    @keyword('Str For DM5')
    def md5(self, init_str):
        """
        md5加密

        example:
        | ${str_for_md5} |  tran2UTF8 |  ${init_str} | 
        """
        m = hashlib.md5()
        m.update(init_str)

        return m.hexdigest()


    @keyword('Eval Dict')
    def eval_dict(self, strInput):
        u"""接收字符串直接转成需要类型,例

        | ${strOutput} |eval dict   | str  |
        """
        strInput = eval(strInput)

        return strInput


    @keyword('Random Num')
    def random_num(self, num):
        """
        随机指定位数的数字

        ``num`` 随机位数

        """
        number = ''
        for i in random.sample(range(10), int(num)):
            number += ''.join(str(i))

        return number


    @keyword('Located User Info')
    def located_user(self,value):
        """
        落库地址查询

        example:
        | ${tb_index} | Located User |  ${data} |
        """
        relation_dict = {(1,251):"1", (251,501):"1", (501,751):"1", (751,1001):"1"}
        
        digest = int(hashlib.md5(str(value).encode()).hexdigest(), 16)
        mod = digest % 1000 + 1
        for k, v in relation_dict.items():
            if k[0]<=mod<k[1]:
                returns = str(digest % 32 + 1).zfill(2)
                return returns
    
    @keyword('Get Current Time')                
    def get_current_time(self):
        """
        获取当前时间
        """
        current_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        return current_time

    @keyword('Unicode To Dict')                
    def uinicode_to_dict(self,input):
        """
        转换为json
        | ${dict} | Unicode To Dict  | ${input_str} |
        """
        inputStr = str(input)
        inputDict = json.loads(inputStr)
        return inputDict

    @keyword('GBK To Unicode')                
    def convert_gbk_2_unicode(self,input):
        """编码转换：GBK转为Unicode"""

        output = str(input).encode('unicode_escape')
        return output

    @keyword('Unicode To GBK')   
    def convert_unicode_2_gbk(self,input):
        """编码转换：Unicode转为GBK"""
        
        # """Linux"""
        output = str(input).encode('utf-8').decode('unicode_escape')
        # """Windows"""
        # output = str(input).encode('unicode_escape').decode('unicode_escape')
        return output
