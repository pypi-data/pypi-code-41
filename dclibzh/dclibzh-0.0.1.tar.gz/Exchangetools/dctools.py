import datetime
from urllib.parse import quote
import hashlib
import hmac
import base64
import  pandas as pd


class getAPIkey():

    def __init__(self,keyid,secretkey,apikeyname,apivars):
        #url是由SignatureVersion&SignatureMethod&AccessKeyId组成

        self.secretkey=secretkey

        self.apilists=['AccessKeyId='+ keyid,'SignatureVersion=2','SignatureMethod=HmacSHA256',]
        self.apivars=apivars
        self.apikeyname=apikeyname



    def getsecretkey(self):
        # api验证需要的时间（经过以YYYY-MM-DDThh:mm:ss格式添加并且进行 URI 编码）
        dctime = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
        dctime = quote(dctime, 'utf-8')

        # api验证需要添加的时间和条件，apivars是条件的列表
        apilist=self.apilists.copy()
        apilist.append('Timestamp='+dctime)
        if not self.apivars==['']:
            for  apivars in self.apivars:
                apilist.append(apivars )

        # api验证需要经过排序之后
        apilists=sorted(apilist)

        #按照以上顺序，将各参数使用字符 “&” 连接，self.apikeyname是get\n代码
        apiurlstr= '&'.join(apilists)
        keyurl=self.apikeyname+apiurlstr


        #用上一步里生成的 “请求字符串” 和你的密钥 (Secret Key) 生成一个数字签名
        #数字签名在URL编码后
        secretkeysha=hmac.new(self.secretkey.encode('utf-8'),keyurl.encode('utf-8'),digestmod=hashlib.sha256).digest()
        secretkeystr = base64.b64encode(secretkeysha).decode()
        secretkeystr =quote(secretkeystr,'utf-8')

        #最后得到一个带有所有参数的代码
        secretkeystr= 'Signature='+secretkeystr
        secretkeystr=apiurlstr+r'&'+secretkeystr




        return secretkeystr



    def postsecretkey(self):
        # api验证需要的时间（经过以YYYY-MM-DDThh:mm:ss格式添加并且进行 URI 编码）
        dctime1 = datetime.datetime.utcnow()
        dctime=dctime1.strftime('%Y-%m-%dT%H:%M:%S')
        dctime = quote(dctime, 'utf-8')
        apilists=self.apilists.copy()

        # api验证需要添加的时间和条件，apivars是条件的列表
        apilists.append('Timestamp='+dctime)

        # api验证需要经过排序之后
        apilists=sorted(apilists)

        #按照以上顺序，将各参数使用字符 “&” 连接，self.apikeyname是get\n代码
        apiurlstr= '&'.join(apilists)

        keyurl=self.apikeyname+apiurlstr


        #用上一步里生成的 “请求字符串” 和你的密钥 (Secret Key) 生成一个数字签名
        #数字签名在URL编码后
        secretkeysha=hmac.new(self.secretkey.encode('utf-8'),keyurl.encode('utf-8'),digestmod=hashlib.sha256).digest()
        secretkeystr = base64.b64encode(secretkeysha).decode()
        secretkeystr =quote(secretkeystr,'utf-8')
        secretkeystr = 'Signature=' + secretkeystr
        secretkeystr = apiurlstr + r'&' + secretkeystr

        return secretkeystr


#数据专用对象
class exchangetopandasdf():

#转变lists为Datafram值
    def exchangetopandasdftrue(self, orginaldatalists):

        orginalkeys = []
        finallydatadic = {}
        if not orginaldatalists == []:
            orginaldatadics = orginaldatalists[0]

            for orginaldatadic in orginaldatadics.keys():
                orginalkeys.append(orginaldatadic)

            for orginalkey in orginalkeys:
                finallydatadic[orginalkey] = []
                finallydatalist = []
                for orginaldatalist in orginaldatalists:
                    finallydatalist.append(orginaldatalist[orginalkey])

                finallydatadic[orginalkey] = finallydatalist

            df = pd.DataFrame(finallydatadic)
            print(df)
            return df
        else:
            df = pd.DataFrame()
            return df

#判断是否属于lists，如果是dic，继续获取list，如果不是，就是错误值
    def exchangetopandasdf(self,orginaldatalists):
        # self.exchangetopandasdftrue(orginaldatalists)

        if type(orginaldatalists) == type([]):
          df=self.exchangetopandasdftrue(orginaldatalists)
          return df


        elif type(orginaldatalists) == type({}):
            orginalkeys = []
            for  orginaldatalist in orginaldatalists.keys():
                orginalkeys.append(orginaldatalist)

            finallydatalist=orginaldatalists[orginalkeys[-1]]

            self.exchangetopandasdf(finallydatalist)

        else:
            return("找不到类型")







































