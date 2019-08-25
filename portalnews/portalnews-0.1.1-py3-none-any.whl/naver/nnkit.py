from urllib.parse import urlparse, parse_qs


def get_oid_aid_from_url(url):
    o = urlparse(url)
    q = parse_qs(o.query)
    return q['oid'][0], q['aid'][0]

if __name__ == '__main__':
    oid, aid = get_oid_aid_from_url('https://news.naver.com/main/ranking/read.nhn?mid=etc&sid1=111&rankingType=popular_day&oid=002&aid=0002096746&date=20190710&type=1&rankingSectionId=100&rankingSeq=1&m_view=1&includeAllCount=true&m_url=%2Fcomment%2Fall.nhn%3FserviceId%3Dnews%26gno%3Dnews002%2C0002096746%26sort%3Dlikability')
    print(oid, aid)