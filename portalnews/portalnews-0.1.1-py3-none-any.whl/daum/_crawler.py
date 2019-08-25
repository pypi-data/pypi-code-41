import dateutil.parser
import itertools
import requests
from .. import GenericPortalNewsCrawler
from . import parser
from .const import *
import lxml.html
import warnings

class DaumNewsCrawler(GenericPortalNewsCrawler):
    def __init__(self, session=None):
        self._sess = session or requests.Session()
        self._sess.headers['referer'] = 'https://media.daum.net'
        self._authorize()

    def _authorize(self):
        r = self._sess.get(
            url='https://comment.daum.net/oauth/token',
            params=dict(client_id=DEFAULT_CLIENT_ID, grant_type='alex_credentials')
        )
        token = r.json()['access_token']
        self._sess.headers['Authorization'] = f'Bearer {token}'

    # -----------------------------
    @staticmethod
    def get_daily_articles_by_category(date, category=None, subcategory=None, start_page=None):
        date = dateutil.parser.parse(date).strftime('%Y%m%d')

        if not category and subcategory:
            # TODO: auto matching
            raise ValueError('Subcategory must defined with (main) category')

        if not category and not subcategory:
            url = 'https://media.daum.net/breakingnews'
        elif not subcategory:
            url = 'https://media.daum.net/breakingnews/{}'.format(category)
        else:
            url = 'https://media.daum.net/breakingnews/{}/{}'.format(category, subcategory)

        params = dict(regDate=date)

        daily_articles = []
        for page in itertools.count(start_page or 1):
            params['page'] = page
            r = requests.get(url, params=params)
            articles, is_last_page = parser.parse_breakingnews(r)
            daily_articles.extend(articles)
            if is_last_page:
                break

        timestamp_prefix = dateutil.parser.parse(date).strftime('%Y-%m-%d ')
        for a in daily_articles:
            a['timestamp'] = timestamp_prefix + a['timestamp']

        return daily_articles


    @staticmethod
    def get_daily_main_articles(date, tab_cate):
        if tab_cate not in ['NE', 'EN', 'SP']:
            raise ValueError('tab_cate must be NE, EN or SP')
        elif tab_cate == 'NE':
            if date < '20081014':
                warnings.warn('다음 뉴스 메인기사 목록은 2008-10-14 이후 공개되어있습니다.')
        elif date < '20090515':
            warnings.warn('다음 연예/스포츠 메인기사 목록은 2009-05-15 이후 공개되어있습니다.')

        params = dict(regDate=date, tab_cate=tab_cate)
        main_articles = []
        for page in itertools.count(1):
            params['page'] = page
            r = requests.get('https://media.daum.net/newsbox', params=params)
            articles, is_last_page = parser.parse_newsbox(r)
            main_articles.extend(articles)
            if is_last_page:
                break

        return main_articles


    @staticmethod
    def get_daily_most_read_articles(date, category='', categories=None):
        if categories:
            category = ','.join(categories)
        params = {'include': category, 'regDate': date}
        r = requests.get('https://media.daum.net/ranking/popular', params=params)
        return parser.parse_ranking(r)

    @staticmethod
    def get_daily_most_commented_articles(date, category='', categories=None):
        if categories:
            category = ','.join(categories)
        params = {'include': category, 'regDate': date}
        r = requests.get('https://media.daum.net/ranking/bestreply', params=params)
        return parser.parse_ranking(r)

    @staticmethod
    def get_daily_most_perused_articles(date, category, categories=None):
        # https://media.daum.net/proxy/api/mc2/contents/ranking.json?clusterId=552953&service=&rankingField=dri&pageSize=50
        raise NotImplementedError()

    # -----------------------------
    @staticmethod
    def get_article_content(post_key):
        # TODO: parse page?
        resp = requests.get(url='https://news.v.daum.net/v/{}'.format(post_key), params={'f': 'm'})
        tree = lxml.html.fromstring(resp.text)
        head = tree.find('.//div[@class="head_view hcg_news_mobile_bodyHead"]')
        press = head.find('.//em[@class="info_cp"]/a/img').get('alt').strip()
        title = head.find('.//h3[@class="tit_view"]').text.strip()
        other = head.xpath('.//span[@class="txt_info"]/text()')
        print(press, title, other)

        body = tree.find('.//div[@id="newsContents"]')
        return lxml.html.tostring(head, encoding='unicode') + lxml.html.tostring(body, encoding='unicode')

    @staticmethod
    def get_article_reactions(cate, post_key, verbose=False):
        if cate not in {'news', 'sports', 'entertain'}:
            raise ValueError('cate must be one of [news, sports, or entertain]')
        resp = requests.get('https://like.daum.net/item/{}/{}.json'.format(cate, post_key))
        like = resp.json()
        if like['status'] != 200:
            raise Exception('response status is not 200', resp.url)

        if verbose:
            return like
        return like['data']['likeCount']

    # -----------------------------
    def get_comment_metadata(self, post_key):
        """
        다음 뉴스 포스트 키 두가지 유형 존재
        일반 유형 예시 : 20190318155900077
        해시 유형 예시 : a6qCbz8eQ5
        :param post_key:
        :return:
        """
        r = self._sess.get('https://comment.daum.net/apis/v1/posts/@'+str(post_key))

        if r.status_code == 400:
            raise ValueError('Invalid post key:', post_key, r.url)
        elif r.status_code == 401:
            self._authorize()
            return self.get_post(post_key)
        elif r.status_code != 200:
            raise Exception('Invalid post key:', post_key, r.url)

        post = r.json()
        if len(post_key) == 17:
            return post

        numeric_post_key = post['url'].rsplit('/', 1)[-1]
        return self.get_post(numeric_post_key)

    # -----------------------------
    def get_all_comments(self, post_key, page_size=10000):
        all_comments = []
        for page in itertools.count(1):
            batch = self._get_comments(post_key, page, page_size=page_size)
            all_comments.extend(batch)
            if len(batch) < page_size:
                break
        return all_comments

    def _get_comments(self, post_key, page, page_size):
        params = dict(
            parentId=0,
            limit=page_size,
            offset=(page - 1) * page_size,
            sort='CHRONOLOGICAL',
            isInitial=False
        )

        r = self._sess.get(
            'https://comment.daum.net/apis/v1/posts/@{}/comments'.format(post_key),
            params=params
        )

        return r.json()

    def get_all_replies(self, comment_id, page_size=10000):
        all_replies = []
        for page in itertools.count(1):
            batch = self._get_replies(comment_id, page, page_size)
            all_replies.extend(batch)
            if len(batch) < page_size:
                break
        return all_replies

    def _get_replies(self, comment_id, page, page_size):
        params = dict(
            limit=page_size,
            offset=(page - 1) * page_size,
            sort='CHRONOLOGICAL',
        )

        r = self._sess.get(
            'https://comment.daum.net/apis/v1/comments/{}/children'.format(comment_id),
            params=params
        )

        return r.json()
    # -----------------------------
    @staticmethod
    def _get_article_info_kaede(post_key):
        raise NotImplementedError
        temp = 'author,issuecluster,series,planning,tv,video'.split(',')
        try:
            params = dict(
                paths='news,'+post_key,
                clusterType='video',
                #clusterSize=1,
                #contentsType='news',
                #contetnsCount=5
            )

            r = requests.get(
                url='https://api.v.kakao.com/p/346KaedeS2',
                params=params
            )
        except:
            raise
        else:
            return r.json()
