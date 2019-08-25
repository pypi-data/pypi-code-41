import lxml.html
from urllib.parse import urlparse
from requests.models import Response
import dateutil.parser
import warnings
from requests import Session


class ElemParser:
    @staticmethod
    def parse_title_li(elem):
        url = 'https://news.nate.com/' + elem.find('a').get('href').strip()
        office = elem.find('span[@class="medium"]').text.strip()
        timestamp = elem.find('span[@class="medium"]/em').text.strip()
        try:
            title = elem.find('a').text.strip()
        except AttributeError:
            title = ''

        content_type = elem.xpath('img/@alt')

        return dict(url=url, timestamp=timestamp, office=office, title=title, type=content_type)

    @staticmethod
    def parse_desktop_comment_item(elem):
        comment_id = elem.get('id').rsplit('_', 1)[1]
        user_id = eval(elem.find('dt/span[@class="nameui"]').get('onfocus').strip('show_cmtuser_ui;'))[-1]
        user_name = elem.find('dt/span[@class="nameui"]').text.strip()
        timestamp = elem.xpath('dt/span[@class="date"]/text()')[0].strip()
        upvotes, downvotes = [int(n.replace(',', '')) for n in elem.xpath('dd[@class="opinion"]/div/p/strong/text()')]
        from_mobile = bool(elem.xpath('dd/img[@class="mobileRe"]'))
        text = ''.join(elem.xpath('dd[@class="usertxt"]/text()')).strip()
        try:
            reply_count = int(elem.xpath('dd[@class="reples"]/a/span/text()')[0].replace(',', ''))
        except IndexError:
            reply_count = 0
        comment = dict(
            commentId=comment_id,
            userId=user_id,
            userName=user_name,
            timestamp=timestamp,
            upvotes=upvotes,
            downvotes=downvotes,
            from_mobile=from_mobile,
            text=text,
            reply_count=reply_count,
        )

        return comment
        # raise NotImplementedError

    @staticmethod
    def parse_paging_div(elem):
        raise NotImplementedError

    @staticmethod
    def parse_date_paging_div(elem):
        raise NotImplementedError


def parse_title_list(r: Response):
    """

    :param r:
    :return:
    """
    tree = lxml.html.fromstring(r.text)
    main = tree.find('.//div[@id="newsContents"]')
    artc_list = main.xpath('.//div[@class="postSubject"]/ul[@class="mduSubject"]/li')
    articles = [ElemParser.parse_title_li(item) for item in artc_list]

    page_navi = list(main.xpath('div[@class="paging"]/*'))
    is_last_page = False
    try:
        if page_navi[-1].tag == 'span':
            if list(page_navi[-1])[-1].tag == 'strong':
                is_last_page = True
    except IndexError:
        is_last_page = True
    #is_last_page = page_navi[-1].tag != 'a'  # TODO: IndexError

    date_navi = list(main.xpath('div[@class="weekpagingNotCal f_clear"]/*[not(self::span)]'))
    curr_date_idx = [e.tag for e in date_navi].index('strong')
    next_date = None if curr_date_idx == 0 else date_navi[curr_date_idx - 1].get('href')[-8:]
    prev_date = None if curr_date_idx == len(date_navi) - 1 else date_navi[curr_date_idx + 1].get('href')[-8:]

    return articles, is_last_page, next_date, prev_date


def parse_article_up_down(r):
    tree = lxml.html.fromstring(r.text)
    main = tree.find('.//div[@class="articleUpDown"]')
    up, down = map(int, main.xpath('.//em/text()'))
    return dict(up_cnt=up, down_cnt=down)


def parse_comment_page(r, as_html):
    tree = lxml.html.fromstring(r.text)
    comment_elems = tree.xpath('.//div[@class="cmt_list"]/dl')

    if as_html:
        comments = [lxml.html.tostring(c, encoding='unicode') for c in comment_elems]
    else:
        comments = [ElemParser.parse_desktop_comment_item(e) for e in comment_elems]

    paging = tree.xpath('.//div[@class="paging_wrap"]/*')
    is_last_page = True if not paging or paging[-1].get('class') == 'on' else False

    return comments, is_last_page

def parse_desktop_ranking_page(r, ranking_type):
    def parse_top5(elem):
        #elem = elem.find('div')
        link = elem.find('.//a')
        href = 'https:' + link.get('href')
        title = link.find('.//strong').text
        #artc_sq = href.split('/')[-1].split('?')[0]
        office = elem.find('.//span[@class="medium"]').text
        count = elem.xpath('.//span/em/text()')

        news = dict()
        news['title'] = title
        news['url'] = href
        #news['artc_sq'] = artc_sq
        news['office'] = office
        try:
            news[ranking_type] = int(count[0].replace(',', ''))
        except (ValueError, IndexError):
            pass

        return news

    def parse_rest(elem):
        link = elem.find('a')
        href = 'https:' + link.get('href')
        title = link.text
        #artc_sq = href.split('/')[-1].split('?')[0]
        office = elem.find('span[@class="medium"]').text
        count = elem.xpath('.//span/em/text()')

        news = dict()
        news['title'] = title
        news['url'] = href
        #news['artc_sq'] = artc_sq
        news['office'] = office
        try:
            news[ranking_type] = int(count[0].replace(',', ''))
        except (ValueError, IndexError):
            pass

        return news

    tree = lxml.html.fromstring(r.text)
    #top5 = tree.xpath('//*[@id="newsContents"]/div/div[2]/div')
    #rest = tree.xpath('//*[@id="newsContents"]/div/div[3]/ul/li')

    top5 = tree.xpath('//*[@id="newsContents"]/div/div[@class="postRankSubjectList f_clear"]/div')
    rest = tree.xpath('//*[@id="newsContents"]/div/div[@id="postRankSubject"]/ul/li')

    return [parse_top5(e) for e in top5] + [parse_rest(e) for e in rest]


if __name__ == '__main__':
    import requests
    from pprint import pprint

    #r = requests.get('https://news.nate.com/recent?cate=pol&type=t&date=20190711&page=80')
    #pprint(parse_title_list(r))

    #r = requests.get('https://comm.news.nate.com/view/updown?aid=20190714n00983', verify=False)
    #print(parse_article_up_down(r))

    ##r = requests.get('https://comm.news.nate.com/Comment/ArticleComment/list?artc_sq=20190714n00983&order=O&cmtr_fl=0&prebest=0&clean_idx=&user_nm=&fold=0&mid=n0000&domain=&argList=0&best=0&return_sq=&connectAuth=N&page=2#comment', verify=False)
    # print(parse_comment_page(r))

    #print(lxml.html.fromstring('<br></br>') == lxml.html.fromstring('<br></br>'))

    r = requests.get('https://news.nate.com/rank/cmt')
    #r = requests.get('https://news.nate.com/rank/pop?sc=pol&p=week&date=20190704')
    pprint(parse_desktop_ranking_page(r))