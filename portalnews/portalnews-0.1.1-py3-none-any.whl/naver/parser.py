import lxml.html
from urllib.parse import urlparse
from requests.models import Response
import dateutil.parser
import warnings


def standardize_timestamp(timestamp):
    if '오전' in timestamp:
        timestamp = timestamp.replace('오전', '') + ' AM'
    elif '오후' in timestamp:
        timestamp = timestamp.replace('오후', '') + ' PM'
    return dateutil.parser.parse(timestamp).strftime('%Y-%m-%d %H:%M')


class PageParser:
    pass


class ElemParser:
    @staticmethod
    def parse_ranking_popular_item(li):
        a = li.find('.//a')
        url = a.get('href')
        if not url.startswith('http'):
            url = 'https://news.naver.com' + url
        title = a.get('title')
        office = li.find('.//div[@class="ranking_office"]').text

        item = dict(url=url, title=title, office=office)
        try:
            view_count = int(li.find('.//div[@class="ranking_view"]').text.replace(',', ''))
            item['view_count'] = view_count
        except AttributeError:
            pass
        return item

    @staticmethod
    def parse_mobile_ranking_item(li):
        url = 'http://m.news.naver.com' + li.find('.//a').get('href')
        title = li.find('.//div[@class="commonlist_tx_headline"]').text
        view_count = int(li.find('.//div[@class="commonlist_tx_visit"]').text_content()[3:].replace(',', ''))
        item = dict(url=url, title=title, view_count=view_count)
        return item

    @staticmethod
    def parse_memo_ranking_item(elem):
        url = 'http://m.news.naver.com' + elem.find('.//a').get('href')
        title = elem.find('.//div[@class="commonlist_tx_headline"]').text
        comment_count = int(elem.find('.//div[@class="commonlist_tx_reply"]').text_content()[5:].replace(',', ''))
        item = dict(url=url, title=title, comment_count=comment_count)
        return item

    @staticmethod
    def parse_title_item(elem):
        url       = elem.find('a').get('href').strip()
        timestamp = elem.find('span[@class="date"]').text.strip()
        office    = elem.find('span[@class="writing"]').text.strip()
        has_photo = elem.find('i[@class="icon_photo"]') is not None
        is_video  = elem.find('string[@class="r_ico r_vod_txt"]') is not None

        try:
            title = elem.find('a').text.strip()
        except AttributeError:
            title = ''

        try:
            on_newspaper = elem.find('span[@class="newspaper_info"]').get('title')
        except AttributeError:
            on_newspaper = False

        return dict(
            url=url, timestamp=timestamp, office=office, title=title,
            has_photo=has_photo,
            is_video=is_video,
            on_newspaper=on_newspaper)

    @staticmethod
    def parse_desktop_ranking_item(elem):
        raise NotImplementedError

    @staticmethod
    def parse_main_text_item(elem):
        href = elem.find('a').get('href')
        title = elem.find('a').text
        office = elem.find('span/span[@class="writing"]').text
        article = dict(url=href, title=title, office=office, type='text')

        try:
            expose = elem.find('span/span[@class="eh_edittime"]').text
        except AttributeError:
            pass
        else:
            article['expose'] = expose

        return article

    @staticmethod
    def parse_main_photo_tv_item(elem):
        href = elem.find('a').get('href')
        title = elem.find('a/em').text
        office = elem.find('span[@class="eh_by"]').text
        article = dict(url=href, title=title, office=office, type='photo')

        try:
            expose = elem.find('span[@class="eh_time"]').text
        except AttributeError:
            pass
        else:
            article['expose'] = expose

        return article



def parse_ranking_popular_list(r):
    html = lxml.html.fromstring(r.text)
    ol = html.find('.//ol[@class="ranking_list"]')
    return [ElemParser.parse_ranking_popular_item(li) for li in ol]


def parse_mobile_ranking_list(r):
    html = lxml.html.fromstring(r.text)
    ul = html.find('.//ul[@class="commonlist"]')
    return [ElemParser.parse_mobile_ranking_item(li) for li in ul]


def parse_memo_ranking_list(r):
    html = lxml.html.fromstring(r.text)
    ul = html.find('.//ul[@class="commonlist"]')
    return [ElemParser.parse_memo_ranking_item(li) for li in ul]


def parse_main_history_mainnews_photo_tv(r: Response):
    """
    SAMPLE URL
    https://news.naver.com/main/history/mainnews/photoTv.nhn?date=2014-04-30

    :param r:
    :return:
    """
    tree = lxml.html.fromstring(r.text)
    articles = [ElemParser.parse_main_photo_tv_item(item) for item in tree.xpath('ul/li')]
    last_page = int(tree.find('input').get('value'))
    return articles, last_page


def parse_main_history_mainnews_text(r: Response):
    """
    SAMPLE URL
    https://news.naver.com/main/history/mainnews/text.nhn?date=2014-04-30

    :param html:
    :return:
    """
    tree = lxml.html.fromstring(r.text)
    articles = [ElemParser.parse_main_text_item(item) for item in tree.xpath('ul/li')]
    last_page = int(tree.find('input').get('value'))
    return articles, last_page


def parse_main_list(r: Response):
    """
    SAMPLE URL
    https://news.naver.com/main/list.nhn?mode=LS2D&sid2=249&sid1=102&mid=sec&listType=title&date=20190616&page=3
    :param r: Requests response
    :return:
    """
    tree = lxml.html.fromstring(r.text)
    main = tree.find('.//div[@id="main_content"]')
    artc_list = main.xpath('div[@class="list_body newsflash_body"]/ul/li')
    articles = [ElemParser.parse_title_item(item) for item in artc_list]

    page_navi = list(main.xpath('div[@class="paging"]/*'))
    is_last_page = page_navi[-1].tag != 'a'  # TODO: IndexError

    date_navi = list(main.xpath('div[@class="pagenavi_day"]/*[not(@class="devidebar")]'))
    curr_date_idx = [e.tag for e in date_navi].index('span')
    next_date = None if curr_date_idx == 0 else date_navi[curr_date_idx-1].get('href')[-8:]
    prev_date = None if curr_date_idx == len(date_navi) - 1 else date_navi[curr_date_idx+1].get('href')[-8:]

    return articles, is_last_page, next_date, prev_date


def parse_article(r: Response):
    tree = lxml.html.fromstring(r.text)

    try:
        title = tree.xpath("//meta[@property='og:title']/@content")[0]
        # description = tree.xpath("//meta[@property='og:description']/@content")[0]
    except IndexError:
        raise Exception("WRONG META INFO", r.url)

    ''' GET TIMESTAMPS '''
    o = urlparse(r.url)
    if o.netloc.startswith('m.') or o.netloc.startswith('n.'):
        # ['m.news.naver.com', 'm.entertain.naver.com', 'm.sports.naver.com']
        timestamps = tree.xpath('//span[@class="media_end_head_info_datestamp_time"]/text()')
    elif o.netloc == 'news.naver.com':
        timestamps = tree.xpath('//span[@class="t11"]/text()')
    elif o.netloc == 'entertain.naver.com':
        timestamps = tree.xpath('//span[@class="author"]/em/text()')
    elif o.netloc == 'sports.news.naver.com':
        timestamps = tree.xpath('//div[@class="news_headline"]/div[@class="info"]/span/text()')
        timestamps = [t[5:] for t in timestamps]
    else:
        raise NotImplementedError('unknown netloc:', r.url)
    timestamps = [standardize_timestamp(t) for t in timestamps]

    ''' GET CATEGORIES '''
    if 'entertain' in o.netloc or 'entertain' in o.path:
        categories = ['연예']
    elif 'sports' in o.netloc:
        categories = ['스포츠']
    elif o.netloc.startswith('m.news'):
        categories = tree.xpath('//em[@class="media_end_categorize_item"]/text()')
    elif o.netloc == 'news.naver.com':
        categories = tree.xpath('//em[@class="guide_categorization_item"]/text()')
    else:
        raise NotImplementedError('unknown netloc:', r.url)

    ''' GET BODY '''
    if o.netloc.startswith('news.naver'):
        body = tree.find('.//*[@id="articleBodyContents"]')
    elif o.netloc.startswith('m.news') or o.netloc.startswith('n.news'):
        body = tree.find('.//*[@id="dic_area"]')
    elif o.netloc.startswith('entertain'):
        body = tree.find('.//*[@id="articeBody"]')
    elif o.netloc.startswith('m.sports'):
        body = tree.find('.//*[@id="ct"]/div[@class="newsct_body"]/article/div/div/font')
    elif o.netloc.startswith('sports'):
        body = tree.find('.//*[@id="newsEndContents"]')
    else:
        raise NotImplementedError('unknown netloc:', r.url)

    try:
        body_raw = lxml.html.tostring(body, encoding='utf-8').decode()
    except TypeError:
        warnings.warn('Maybe deleted article: {}'.format(r.url))
        return dict(url=r.url, deleted=True)

    paragraphs = [l.strip() for l in body.xpath('text()') if l.strip()]

    created_at = timestamps[0]
    updated_at = timestamps[1] if len(timestamps) > 1 else None

    return dict(
        url=r.url,
        createdAt=created_at,
        updatedAt=updated_at,
        title=title,
        categories=categories,
        paragraphs=paragraphs,
        body_raw=body_raw
    )





if __name__ == '__main__':
    import requests
    from pprint import pprint
    #r = requests.get('https://news.naver.com/main/history/mainnews/photoTv.nhn?date=2014-04-30')
    #pprint(parse_main_history_mainnews_photoTv(r))

    #r = requests.get('https://news.naver.com/main/history/mainnews/text.nhn?date=2014-04-30')
    #pprint(parse_main_history_mainnews_text(r))

    #r = requests.get('https://news.naver.com/main/list.nhn?mode=LSD&mid=sec&sid1=102&listType=title&date=20180719')
    #pprint(parse_main_list(r))

    '''
    r = requests.get('https://m.news.naver.com/read.nhn?oid=001&aid=0010912941&sid1=103&mode=LSD')
    pprint(parse_article(r))
    r = requests.get('https://news.naver.com/main/read.nhn?oid=001&aid=0010912941&sid1=103&mode=LSD')
    pprint(parse_article(r))

    r = requests.get('https://m.entertain.naver.com/ranking/read?oid=213&aid=0001047172')
    pprint(parse_article(r))
    r = requests.get('https://entertain.naver.com/ranking/read?oid=213&aid=0001047172')
    pprint(parse_article(r))
    r = requests.get('https://m.sports.naver.com/golf/news/read.nhn?oid=014&aid=0004055458')
    pprint(parse_article(r))

    r = requests.get(
        'https://sports.news.naver.com/sports/index.nhn?ctg=ranking_news&mod=read&ranking_type=popular_day&date=20120710&office_id=109&article_id=0002378750')
    pprint(parse_article(r))

    r = requests.get('https://news.naver.com/main/ranking/read.nhn?rankingType=popular_day&oid=039&aid=0000125295&date=20040420&type=1&rankingSectionId=000&rankingSeq=1')
    pprint(parse_article(r))
    #'''