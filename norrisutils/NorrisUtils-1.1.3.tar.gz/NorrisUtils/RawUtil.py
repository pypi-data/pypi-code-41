# -*- coding: utf-8 -*-

"""
Norris.RawUtil
~~~~~~~~~~~~

This module implements the Requests API.

:copyright: (c) 2018 by Alaric Norris.
:license: Apache2, see LICENSE for more details.
"""


class RawUtil:
    # 核心功能
    def _extractRawDictCore(this, items, splitItemBy, dict=None):

        """Constructs and sends a :class:`Request <Request>`.

        :param method: method for the new :class:`Request` object.
        :param url: URL for the new :class:`Request` object.
        :param params: (optional) Dictionary or bytes to be sent in the query string for the :class:`Request`.
        :param data: (optional) Dictionary or list of tuples ``[(key, value)]`` (will be form-encoded), bytes, or file-like object to send in the body of the :class:`Request`.
        :param json: (optional) A JSON serializable Python object to send in the body of the :class:`Request`.
        :type timeout: float or tuple
        :param allow_redirects: (optional) Boolean. Enable/disable GET/OPTIONS/POST/PUT/PATCH/DELETE/HEAD redirection. Defaults to ``True``.
        :type allow_redirects: bool
        :return: :class:`Response <Response>` object
        :rtype: requests.Response

        Usage::

          >>> import NorrisUtils.RawUtil
          >>> rawutil = NorrisUtils.RawUtil.RawUtil()
          >>> rawutil._extractRawDict('asdf=a,adfasf=33as,zcxv=a123')
          <Response [200]>
        """

        # By using the 'with' statement we are sure the session is closed, thus we
        # avoid leaving sockets open which can trigger a ResourceWarning in some
        # cases, and look like a memory leak in others.
        try:

            if (items == None or items == [] or items == {}):
                return {}
            if dict == None:
                dict = {}
            for kv in items:
                split = kv.split(splitItemBy)
                if len(split) == 2:
                    if dict.get(split[0], -1) == -1:
                        dict[split[0].strip()] = split[1].strip()
                    else:
                        pass
                else:
                    pass
            return dict
        except:
            return dict

    def _extractRawDict(this, src, dict=None, splitBy=',', splitBy2='='):
        """提取Raw信息中的dict

        :param src: 要提取的原文
        :param dict: 可以接受原有的dict来拼接
        :param splitBy: 分行所用的分隔符
        :param splitBy2: 分Key-Value所用的分隔符
        :return: :class:`Dict` object
        :rtype: dict

        Usage::

          >>> import NorrisUtils.RawUtil
          >>> rawutil = NorrisUtils.RawUtil.RawUtil()
          >>> rawutil._extractRawDict('asdf=a,adfasf=33as,zcxv=a123',splitBy=',')
        """
        try:
            if (src == None or src == ''):
                return {}
            if dict == None:
                dict = {}
            items = src.split(splitBy)
            return this._extractRawDictCore(items, splitBy2, dict)
        except:
            return {}

    def _extractHeaderDict(this, src, dict={}):
        """提取headers dict
        :param src: 要提取的原文
        :return: :class:`Dict` object
        :rtype: dict

        Usage::

          >>> import NorrisUtils.RawUtil
          >>> rawutil = NorrisUtils.RawUtil.RawUtil()
          >>> rawutil._extractHeaderDict('''reqChannelId: boc-mlife-app\
Content-Type: application/x-www-form-urlencoded; charset=gbk\
Content-Length: 328\
Host: mlife.jf365.boc.cn\
Connection: Keep-Alive\
Accept-Encoding: gzip\
Cookie: JSESSIONID=000X-PjO7dg-OfJ7:cluserver8\
User-Agent: okhttp/3.5.0''')

        """
        if (isinstance(src, str)):
            return this._extractRawDict(src, splitBy='\n', splitBy2=': ', dict=dict)
        else:
            return this._extractRawDictCore(src, splitItemBy=': ', dict=dict)

    def _extractCookieDict(this, src, dict={}):
        """提取cookies dict
        :param src: 要提取的原文
        :return: :class:`Dict` object
        :rtype: dict

        Usage::
          >>> import NorrisUtils.RawUtil
          >>> rawutil = NorrisUtils.RawUtil.RawUtil()
          >>> rawutil._extractCookieDict('JSESSIONID=0F_wX-PjO7dg-OfJ7:cluserver8')
        """
        return this._extractRawDict(src, splitBy=';', dict=dict)

    def _extractParamsDict(this, src):
        """提取请求参数 dict
        :param src: 要提取的原文
        :return: :class:`Dict` object
        :rtype: dict

        Usage::
          >>> import NorrisUtils.RawUtil
          >>> rawutil = NorrisUtils.RawUtil.RawUtil()
          >>> rawutil._extractParamsDict('clientVersion=3.4.0&userPlt=00&sendPlt=jf365&lon=118.81136')
        """
        return this._extractRawDict(src, splitBy='&', splitBy2='=')

    # 提取Cookie长文本
    def _extractCookieString(this, src):
        try:
            headers = this._extractHeaderDict(src)
            return headers['Cookie']
        except:
            return ''

    def extractHeadLine(this, headline):
        return '', ''

    # 自动提取Raw报文 返回 headers params cookies
    def extractFiddlerRaw(this, rawData):
        """全自动提取Fiddler报文
        :param rawData: 要提取的原文
        :return: :class:`RawInfo` RawInfo
        :rtype: RawInfo

        Usage::
          >>> import NorrisUtils.RawUtil
          >>> rawutil = NorrisUtils.RawUtil.RawUtil()
          >>> rawutil.extractFiddlerRaw(''''''POST /AppPrj/integralBalInquire.do HTTP/1.1
reqChannelId: boc-mlife-app
Content-Type: application/x-www-form-urlencoded; charset=gbk
Content-Length: 328
Host: mlife.jf365.boc.cn
Connection: Keep-Alive
Accept-Encoding: gzip
Cookie: JSESSIONID=000Xcluserver8
User-Agent: okhttp/3.5.0

clientVersion=3.4.0&userPlt=00&sendPlt=jf365&lon=118.81136&lat=32.011847&city=北京&cityIdCde=110100&deviceType=1&deviceID=02:00:00:00:00:00&c=&txnId=1FIN010011
'''''')
        """
        rawinfo = RawInfo()
        if (rawData == None or rawData == ''):
            return rawinfo
        # 按行分割成数组
        rawArray = rawData.splitlines()
        # rawinfo.headLine = rawArray[0]
        rawinfo.setHeadLine(rawArray[0])
        headersStrArray = {}
        # 找到空行的位置
        try:
            indexOfEmptyLine = rawArray.index('')
            if (indexOfEmptyLine != 0):
                # 说明有附加参数
                rawinfo.strParams = rawArray[indexOfEmptyLine + 1]
                if (rawinfo.strParams != None and rawinfo.strParams != ''):
                    rawinfo.dictParams = this._extractParamsDict(rawinfo.strParams)
                headersStrArray = rawArray[1:indexOfEmptyLine]
            else:
                headersStrArray = rawArray[1:]
        except:
            headersStrArray = rawArray[1:]
            pass
        rawinfo.dictHeader = this._extractHeaderDict(headersStrArray, dict={})
        rawinfo.strCookie = this._extractCookieString(headersStrArray)
        rawinfo.dictCookie = this._extractCookieDict(rawinfo.strCookie, dict={})
        return rawinfo

    # 自动提取Raw报文 返回 headers params cookies
    def extractCharlesRaw(this, rawData, https=True):
        rawinfo = RawInfo()
        if (rawData == None or rawData == ''):
            return rawinfo
        # 按行分割成数组
        rawArray = rawData.splitlines()
        headersStrArray = {}
        # 找到空行的位置
        try:
            indexOfEmptyLine = rawArray.index('')
            if (indexOfEmptyLine != 0):
                # 说明有附加参数
                rawinfo.strParams = rawArray[indexOfEmptyLine + 1]
                if (rawinfo.strParams != None and rawinfo.strParams != ''):
                    rawinfo.dictParams = this._extractParamsDict(rawinfo.strParams)
                headersStrArray = rawArray[1:indexOfEmptyLine]
            else:
                headersStrArray = rawArray[1:]
        except:
            headersStrArray = rawArray[1:]
            pass
        rawinfo.dictHeader = this._extractHeaderDict(headersStrArray, dict={})
        rawinfo.strCookie = this._extractCookieString(headersStrArray)
        rawinfo.dictCookie = this._extractCookieDict(rawinfo.strCookie, dict={})
        # rawinfo.headLine = rawArray[0]
        rawinfo.setHeadLine(rawArray[0], host=rawinfo.dictHeader['Host'], https=https)
        return rawinfo


class RawInfo:
    headLine = ''
    method = ''
    url = ''
    urls = ''
    strParams = ''
    strCookie = ''
    dictHeader = {}
    dictParams = {}
    dictCookie = {}

    def __init__(this):
        this.headLine = ''
        this.method = ''
        this.url = ''
        this.urls = ''
        this.strParams = ''
        this.strCookie = ''
        this.dictHeader = {}
        this.dictParams = {}
        this.dictCookie = {}
        pass

    def setHeadLine(this, headline, host=None, https=True):
        arrays = headline.split(' ')
        print(arrays)
        this.method = arrays[0]
        if (host == None or arrays[1].startswith('http')):
            this.url = arrays[1]
        else:
            if (https):
                this.url = 'https://' + host + arrays[1]
            else:
                this.url = 'http://' + host + arrays[1]

        pass

    def __str__(this):
        return 'Headline:\t\t' + this.headLine \
               + '\nmethod:\t\t' + str(this.method) \
               + '\nurl:\t\t' + str(this.url) \
               + '\nCookieDict:\t\t' + str(this.dictCookie) \
               + '\nParamsDict:\t\t' + str(this.dictParams) \
               + '\nParamsStr:\t\t' + this.strParams \
               + '\nCookieStr:\t\t' + this.strCookie


rawData = '''POST /AppPrj/integralBalInquire.do HTTP/1.1
reqChannelId: boc-mlife-app
Content-Type: application/x-www-form-urlencoded; charset=gbk
Content-Length: 328
Host: mlife.jf365.boc.cn
Connection: Keep-Alive
Accept-Encoding: gzip
Cookie: JSESSIONID=000Xer8
User-Agent: okhttp/3.5.0

clientVersion=3.4.0&userPlt=00&sendPlt=jf365&lon=118.81136&lat=32.011847&city=北京&cityIdCde=110100&deviceType=1&deviceID=02:00:00:00:00:00&c=&txnId=1FIN010011
'''
