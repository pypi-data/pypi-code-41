import dateutil.parser
import itertools
import requests
import json
import warnings
from . import parser
from .. import GenericPortalNewsCrawler

MAX_PAGE_SIZE = 100
SORT_OPTIONS = ['favorite', 'old', 'reply', 'new', 'relative']


class NaverNewsCrawler(GenericPortalNewsCrawler):
    _DEFAULT_HEADERS = {'referer': 'https://news.naver.com'}

    class CommentCrawler:
        __MAX_PAGE_SIZE = 100
        __SORT_OPTIONS = ['favorite', 'new', 'reply', 'old', 'relative']

    def __init__(self):
        self.session = requests.Session()
        self.session.headers['referer'] = 'https://news.naver.com/'

    # -----------------------------
    @staticmethod
    def get_daily_articles_by_category(date, sid1='001', sid2=''):
        date = dateutil.parser.parse(date).strftime('%Y%m%d')
        daily_articles = []
        if not sid2:
            params = dict(mode='LSD', mid='sec', listType='title', date=date, sid1=sid1)
        else:
            params = dict(mode='LS2D', mid='sec', listType='title', date=date, sid1=sid1, sid2=sid2)

        for page in itertools.count(1):
            params['page'] = page
            r = requests.get('https://news.naver.com/main/list.nhn', params=params)
            articles, is_last_page, _, _ = parser.parse_main_list(r)
            if is_last_page:
                # check if the page contains articles before the date
                articles = [a for a in articles if a['timestamp'][:10].replace('.', '') == date]
                daily_articles.extend(articles)
                break
            else:
                daily_articles.extend(articles)

        for a in daily_articles:
            if '오전' in a['timestamp']:
                a['timestamp'] = a['timestamp'].replace('오전', '') + ' AM'
            elif '오후' in a['timestamp']:
                a['timestamp'] = a['timestamp'].replace('오후', '') + ' PM'
            a['timestamp'] = dateutil.parser.parse(a['timestamp']).strftime('%Y-%m-%d %H:%M')

        return daily_articles[::-1]

    @staticmethod
    def get_daily_main_articles(date):
        date = dateutil.parser.parse(date).strftime('%Y-%m-%d')
        if not '2009-06-07' <= date <= '2019-04-04':
            raise ValueError('해당일자의 메인기사 목록은 제공되지 않습니다')

        main_articles = []
        params = dict(date=date)

        for page in itertools.count(1):
            params['page'] = page
            r = requests.get('https://news.naver.com/main/history/mainnews/text.nhn', params=params)
            articles, last_page = parser.parse_main_history_mainnews_text(r)
            main_articles.extend(articles)
            if page >= last_page:
                break

        for page in itertools.count(1):
            params['page'] = page
            r = requests.get('https://news.naver.com/main/history/mainnews/photoTv.nhn', params=params)
            articles, last_page = parser.parse_main_history_mainnews_photo_tv(r)
            main_articles.extend(articles)
            if page >= last_page:
                break

        return main_articles

    @staticmethod
    def get_daily_most_read_articles(date, sid1, device='desktop'):
        if device == 'desktop':
            return NaverNewsCrawler.get_popular_list(date, sid1)
        elif device == 'mobile':
            return NaverNewsCrawler.get_ranking_list(date, sid1)
        else:
            raise ValueError('device must be desktop or mobile')

    @staticmethod
    def get_daily_most_commented_articles(date, sid1):
        if date < '20140703':
            raise ValueError('최다댓글 기사 목록은 2014-07-03부터 공개되어있습니다.')
        params = {'sid1': sid1, 'date': date}
        r = requests.get('http://m.news.naver.com/memoRankingList.nhn', params=params)
        return parser.parse_memo_ranking_list(r)

    @staticmethod
    def get_ranking_list(date, sid1):
        if date < '2014':
            raise ValueError('모바일 최다조회 기사 목록은 2014년부터 공개되어있습니다.')

        params = {'sid1': sid1, 'date': date}
        r = requests.get('http://m.news.naver.com/rankingList.nhn', params=params)
        return parser.parse_mobile_ranking_list(r)

    @staticmethod
    def get_popular_list(date, sid1):
        if sid1 not in {'000', '100', '101', '102', '103', '104', '105', '107', '106'}:
            warnings.warn('잘못된 sid1 값을 입력하였을 수 있습니다.')
        if date < '20040420':
            raise ValueError('최다조회기사목록은 2004-04-20부터 공개되어 있습니다.')

        params = {'rankingType': 'popular_day', 'sectionId': sid1, 'date': date}
        r = requests.get('http://news.naver.com/main/ranking/popularDay.nhn', params=params)
        return parser.parse_ranking_popular_list(r)

    # -----------------------------
    @staticmethod
    def get_article_content_by_url(url):
        r = requests.get(url)
        try:
            return parser.parse_article(r)
        except Exception as e:
            print(url, e)
            return None

    @staticmethod
    def _sid1_to_prefix(sid1):
        if sid1 == '107':
            return 'SPORTS'
        elif sid1 == '106':
            return 'ENTERTAIN'
        else:
            return 'NEWS'

    @staticmethod
    def get_article_reactions(oid, aid, sid1s=('000', '106', '107'), verbose=False):
        prefixes = sorted(set(NaverNewsCrawler._sid1_to_prefix(s) for s in sid1s))
        url = 'https://news.like.naver.com/v1/search/contents'
        params = dict(q='|'.join('{0}[ne_{1}_{2}]|{0}_MAIN[ne_{1}_{2}]'.format(s, oid, aid) for s in prefixes))

        try:
            r = requests.get(url, params=params).json()
        except requests.exceptions.ConnectionError:
            return NaverNewsCrawler.get_article_reactions(oid, aid, sid1s, verbose)

        if verbose:
            return r
        return {b['serviceId']: {a['reactionType']: a['count'] for a in b['reactions']}
                for b in r['contents'] if b['reactions']}

    @staticmethod
    def _get_comments(oid, aid, page, sort='old', page_size=MAX_PAGE_SIZE, parent_comment_no='', as_string=False,
                      initialize=False, pool='cbox5', ticket='news'):
        if sort not in SORT_OPTIONS + ['LIKE']:
            raise ValueError('Invalid sorting option')

        params = {
            'ticket': ticket,
            'pool': pool,
            'objectId': 'news{},{}'.format(oid, aid),
            '_callback': '_',
            'lang': 'ko',
            'country': 'KR',
            'includeAllStatus': 'true',
            'listType': 'OBJECT',
            'initialize': initialize,
            'page': page,
            'sort': sort,
            'pageSize': page_size,
            'pageType': 'more',
            'indexSize': 10,
            'parentCommentNo': parent_comment_no,
        }

        if pool == 'cbox2':
            params.pop('initialize')
            params.pop('includeAllStatus')

        try:
            r = requests.get(
                url='https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json',
                headers=NaverNewsCrawler._DEFAULT_HEADERS,
                params=params
            )
        except requests.exceptions.ConnectionError:
            r = requests.get(
                url='https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json',
                headers=NaverNewsCrawler._DEFAULT_HEADERS,
                params=params
            )

        if as_string:
            return r.text.strip('_();')

        result = json.loads(r.text.strip('_();'))

        # TODO: handle potential exception
        try:
            if result['code'] != '1000' or not result['success']:
                print(result)
                raise Exception
        except KeyError:
            print(result)
            print(params)
            raise

        return result

    @staticmethod
    def get_comment_metadata(oid, aid):
        r = NaverNewsCrawler._get_comments(oid, aid, 1, page_size=1, initialize=False)
        count = r['result']['count']
        return count

    @staticmethod
    def get_comment_demographics(oid, aid):
        r = NaverNewsCrawler._get_comments(oid, aid, 1, page_size=1, initialize=True)
        d = r['result']['graph']
        return d

    @staticmethod
    def get_all_comments(oid, aid, page_size=MAX_PAGE_SIZE, parent_comment_no=''):
        """

        :param oid:
        :param aid:
        :param include_replies:
        :return:
        """
        try:
            page = 1
            comment_list = []
            comment_more = NaverNewsCrawler._get_comments(oid, aid, page, page_size=page_size, parent_comment_no=parent_comment_no)

            while comment_more['result']['commentList']:
                comment_list.extend(comment_more['result']['commentList'])
                page += 1
                comment_more = NaverNewsCrawler._get_comments(oid, aid, page, page_size=page_size, parent_comment_no=parent_comment_no)

            comment_more['result']['commentList'] = comment_list
            return comment_more

        except KeyError:  # TODO: make a new exception class
            if page_size > 20:
                return NaverNewsCrawler.get_all_comments(oid, aid, page_size=20, parent_comment_no=parent_comment_no)
            elif page_size > 5:
                return NaverNewsCrawler.get_all_comments(oid, aid, page_size=5, parent_comment_no=parent_comment_no)
            elif page_size > 1:
                return NaverNewsCrawler.get_all_comments(oid, aid, page_size=1, parent_comment_no=parent_comment_no)
            else:
                raise

    @staticmethod
    def get_all_replies(oid, aid, parent_comment_no):
        return NaverNewsCrawler.get_all_comments(oid, aid, parent_comment_no=parent_comment_no)
