import requests


# 提取Raw信息中的dict  默认为,分割 =为key value
def extractRawDict(dict, src, splitBy=',', splitBy2='='):
    items = src.split(splitBy)
    return extractRawDictCore(dict, items, splitBy2)


def extractRawDictCore(dict, items, splitBy):
    for kv in items:
        split = kv.split(splitBy)
        if len(split) == 2:
            if dict.get(split[0], -1) == -1:
                dict[split[0].strip()] = split[1].strip()
            else:
                pass
        else:
            pass
    return dict


# 提取headers
def extractHeaders(src):
    if (isinstance(src, str)):
        return extractRawDict({}, src, splitBy='\n', splitBy2=': ')
    else:
        return extractRawDictCore({}, src, splitBy=':')


# 提取Cookie长文本
def extractCookie(src):
    headers = extractHeaders(src)
    return headers['Cookie']


# 提取headers
def extractCookieDict(src):
    cookieStr = extractCookie(src)
    if (cookieStr == None or cookieStr == ''):
        return {}
    return extractRawDict({}, cookieStr, splitBy=';')


# 提取请求参数
def extractParams(str):
    return extractRawDict({}, str, splitBy='&', splitBy2='=')


class RawInfo:
    headLine = ''
    strParams = ''
    strCookie = ''
    dictHeader = {}
    dictParams = {}
    dictCookie = {}

    def __init__(self):
        pass

    pass


# 自动提取Raw报文 返回 headers params cookies
def extractFiddlerRaw(rawData):
    dictHeader = {}
    dictParams = {}
    dictCookie = {}
    strCookie = ''
    strParams = ''
    headLine = ''
    if (rawData == None or rawData == ''):
        return headLine, dictHeader, strParams, dictParams, strCookie, dictCookie
    # 按行分割成数组
    rawArray = rawData.splitlines()
    headLine = rawArray[0]
    headersStrArray = {}
    # 找到空行的位置
    try:
        indexOfEmptyLine = rawArray.index('')
        if (indexOfEmptyLine != 0):
            # 说明有附加参数
            strParams = rawArray[indexOfEmptyLine + 1]
            if (strParams != None and strParams != ''):
                dictParams = extractParams(strParams)
            headersStrArray = rawArray[1:indexOfEmptyLine]
        else:
            headersStrArray = rawArray[1:]
    except:
        headersStrArray = rawArray[1:]
        pass
    dictHeader = extractHeaders(headersStrArray)
    dictCookie = extractCookieDict(headersStrArray)
    strCookie = extractCookie(headersStrArray)
    return headLine, dictHeader, dictParams, dictCookie, strParams, strCookie


# 开放外部调用提取Raw信息中的dict  默认为,分割 =为key value
def externalExtractRawDict(src, dict={}, splitBy=',', splitBy2='='):
    items = src.split(splitBy)
    return extractRawDictCore(dict, items, splitBy2)
