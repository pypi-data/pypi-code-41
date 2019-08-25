import itertools
import json

import dateutil.parser
import lxml.html
import requests

from . import parser
from .. import GenericPortalNewsCrawler


class NateNewsCrawler(GenericPortalNewsCrawler):
    __HEADERS_M_VIEW = {'referer': 'https://m.news.nate.com/view'}
    __URL_M_GET_UP_DOWN = 'https://m.comm.news.nate.com/view/GetUpDown'
    __URL_M_COMMENT_LIST = 'https://m.comm.news.nate.com/view/CommentList'
    __CATEGORIES = ['pol', 'eco', 'soc', 'int', 'its', 'col', 'ent', 'spo']
    __RANKING_SECTIONS = ['all', 'sisa', 'spo', 'ent', 'pol', 'eco', 'soc', 'int', 'its']

    # -----------------------------
    @staticmethod
    def get_daily_articles_by_category(date, cate):
        date = dateutil.parser.parse(date).strftime('%Y%m%d')
        daily_articles = []

        for page in itertools.count(1):
            articles, is_last_page = NateNewsCrawler._get_recent_article_list(date, cate, page)
            daily_articles.extend(articles)
            if is_last_page:
                break

        return daily_articles[::-1]

    @staticmethod
    def _get_recent_article_list(date, cate, page):
        params = dict(type='t', date=date, cate=cate, page=page)
        r = requests.get('https://news.nate.com/recent', params=params)
        articles, is_last_page, next_date, prev_date = parser.parse_title_list(r)
        return articles, is_last_page


    @staticmethod
    def get_daily_main_articles():
        raise NotImplementedError('네이트 뉴스는 메인배열이력을 제공하지 않습니다.')

    @staticmethod
    def get_daily_most_interesting_articles(date, sc):
        # TODO 어제까지만 가능
        if sc not in NateNewsCrawler.__RANKING_SECTIONS:
            raise ValueError('sc must be in', NateNewsCrawler.__RANKING_SECTIONS)

        date = dateutil.parser.parse(date).strftime('%Y%m%d')
        try:
            r1 = requests.get(
                url='https://news.nate.com/rank/interest',
                params={'p': 'day', 'date': date}
            )

            r2 = requests.get(
                url='https://news.nate.com/rank/interest',
                params={'p': 'day', 'date': date, 'page': 2}
            )
        except requests.ConnectionError:
            return NateNewsCrawler.get_daily_most_interesting_articles(date)
        else:
            return parser.parse_desktop_ranking_page(r1, 'interest_index') + \
                   parser.parse_desktop_ranking_page(r2, 'interest_index')

    @staticmethod
    def get_daily_most_read_articles(date, sc):
        if sc not in NateNewsCrawler.__RANKING_SECTIONS:
            raise ValueError('sc must be in', NateNewsCrawler.__RANKING_SECTIONS)

        date = dateutil.parser.parse(date).strftime('%Y%m%d')
        try:
            r = requests.get(
                url='https://news.nate.com/rank/pop',
                params={'sc': sc, 'p': 'day', 'date': date}
            )
        except requests.ConnectionError:
            return NateNewsCrawler.get_daily_most_read_articles(date, sc)
        else:
            return parser.parse_desktop_ranking_page(r, '')

    @staticmethod
    def get_daily_most_commented_articles(date):
        date = dateutil.parser.parse(date).strftime('%Y%m%d')
        try:
            r = requests.get(
                url='https://news.nate.com/rank/cmt',
                params={'p': 'day', 'date': date}
            )
        except requests.ConnectionError:
            return NateNewsCrawler.get_daily_most_commented_articles(date)
        else:
            return parser.parse_desktop_ranking_page(r, 'comment_count')

    @staticmethod
    def get_daily_most_upvoted_articles(date):
        date = dateutil.parser.parse(date).strftime('%Y%m%d')
        try:
            r = requests.get(
                url='https://news.nate.com/rank/updown',
                params={'sc': 'up', 'p': 'day', 'date': date}
            )
        except requests.ConnectionError:
            return NateNewsCrawler.get_daily_most_upvoted_articles(date)
        else:
            return parser.parse_desktop_ranking_page(r, 'upvote_count')

    @staticmethod
    def get_daily_most_downvoted_articles(date):
        date = dateutil.parser.parse(date).strftime('%Y%m%d')
        try:
            r = requests.get(
                url='https://news.nate.com/rank/updown',
                params={'sc': 'down', 'p': 'day', 'date': date}
            )
        except requests.ConnectionError:
            return NateNewsCrawler.get_daily_most_downvoted_articles(date)
        else:
            return parser.parse_desktop_ranking_page(r, 'downvote_count')

    # -----------------------------
    @staticmethod
    def get_article_content(artc_sq):
        resp = requests.get('https://m.news.nate.com/view/'+artc_sq)
        tree = lxml.html.fromstring(resp.text)
        body = tree.find('.//div[@class="news_view"]')
        return lxml.html.tostring(body, encoding='unicode')

    @staticmethod
    def get_article_reactions(artc_sq):
        try:
            r = requests.get(
                url='https://m.comm.news.nate.com/View/GetUpDown',
                params={'aid': artc_sq},
                headers=NateNewsCrawler.__HEADERS_M_VIEW
            )
        except requests.exceptions.ConnectionError:
            return NateNewsCrawler.get_article_reactions(artc_sq)
        else:
            reactions = json.loads(r.text.strip('()'))
            reactions['up_cnt'] = int(reactions['up_cnt'].replace(',', ''))
            reactions['down_cnt'] = int(reactions['down_cnt'].replace(',', ''))
            return reactions

    @staticmethod
    def get_comment_count(artc_sq):
        try:
            r = requests.get(
                url='https://m.comm.news.nate.com/view/CommentList',
                params={'aid': artc_sq},
                headers=NateNewsCrawler.__HEADERS_M_VIEW
            )
        except requests.exceptions.ConnectionError:
            return NateNewsCrawler.get_comment_count(artc_sq)
        else:
            tree = lxml.html.fromstring(r.text)
            count = int(tree.find('.//em[@id="totalcnt"]').text.replace(',', ''))
            return count

    @staticmethod
    def get_comment_metadata(artc_sq):
        comment_count = NateNewsCrawler.get_comment_count(artc_sq)
        return dict(comment_count=comment_count)

    @staticmethod
    def get_all_comments(artc_sq, as_html=True):
        all_comment_htmls = []
        for page in itertools.count(1):
            htmls, is_last_page = NateNewsCrawler._get_comments(artc_sq, page, as_html=as_html)
            all_comment_htmls.extend(htmls)
            if is_last_page:
                break
        return all_comment_htmls  #[::-1]

    @staticmethod
    def _get_comments(artc_sq, page, order='', as_html=False):
        if order not in {'', 'O', 'X'}:
            raise ValueError

        try:
            r = requests.get(
                url='https://comm.news.nate.com/Comment/ArticleComment/list',
                params=dict(artc_sq=artc_sq, order=order, page=page),
                verify=False
            )
        except requests.exceptions.ConnectionError:
            return NateNewsCrawler._get_comments(artc_sq, page, order)
        else:
            return parser.parse_comment_page(r, as_html=as_html)

