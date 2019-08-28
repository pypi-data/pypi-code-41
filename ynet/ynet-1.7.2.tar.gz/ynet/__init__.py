import requests
from os.path import basename
from urllib.parse import urlparse
from datetime import date
import json
from html import unescape


class Comment:

    def __init__(self, article=None, name='', email='', location='', title='', text='', likes=0, commentNum=0, commentDate=None, commentId=0, parentId=0):
        self.article = article
        self.name = name
        self.email = email
        self.location = location
        self.title = title
        self.text = text
        self.likes = likes
        self.commentNum = commentNum
        self.commentDate = commentDate
        self.commentId = commentId
        self.parentId = parentId
        if parentId == 0:
            self.isReply = False
        else:
            self.isReply = True

    def set_to_retrived_comment_format(self):
        self.name = unescape(self.name)
        self.title = unescape(self.title)
        self.text = unescape(self.text)
        return self

    def get_replies(self):
        all_comments = self.article.get_comments()
        for comment in all_comments:
            if comment.parentId == self.commentId:
                yield comment

    def get_parent_comment(self):
        all_comments = self.article.get_comments()
        for comment in all_comments:
            if self.parentId == comment.commentId:
                return comment

    def reply(self, comment):
        r = requests.post(
            self.article.article_uri
            + 'YediothPortal/Ext/TalkBack/CdaTalkBackTrans/0,2499,'
            + self.article.article_id
            + '-0-68-13108-0---'
            + str(self.commentId)
            + ',00.html',
            data={
                'WSGBRWSR':'FF',
                'name': comment.name,
                'email': comment.email,
                'Location': comment.location,
                'title': comment.title,
                'description': comment.text
            }
        )
        return r.text
    
    def post(self, useragent=
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"):
        r = requests.post(
            self.article.article_uri
            + 'YediothPortal/Ext/TalkBack/CdaTalkBackTrans/0,2499,'
            + self.article.article_id
            + '-0-68-546-0---0,00.html',
            data={
                'WSGBRWSR': 'FF',
                'name': self.name,
                'email': self.email,
                'Location': self.location,
                'title': self.title,
                'description': self.text},
            headers={
                'User-Agent': useragent
            }
        )
        return r.text


class Article:

    def __init__(self, article_url: str):
        self.article_url = article_url
        parsed_url = urlparse(article_url)
        self.article_id = basename(parsed_url.path).split(',')[2]
        self.article_uri = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_url)

    def get_comments(self):
        r = requests.get(
            self.article_uri
            + "Ext/Comp/ArticleLayout/Proc/ShowTalkBacksAjax/v2/0,12990,"
            + self.article_id
            + "-desc-68-0-1,00.html",
            headers={
                'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36"
            }
        ).text
        comments_json = json.loads(r)['rows']
        for comment_dict in comments_json:
            _comment_date = comment_dict['the_date'].split('.')

            comment_date = date(
                year=int(_comment_date[2]),
                month=int(_comment_date[1]),
                day=int(_comment_date[0])
            )
            yield Comment(
                article=self,
                name=comment_dict['name'],
                title=comment_dict['title'],
                text=comment_dict['text'],
                location=comment_dict['location'],
                commentDate=comment_date,
                commentNum=comment_dict['tc'],
                likes=comment_dict['ts'],
                commentId=comment_dict['id'],
                parentId=comment_dict['parent_id']
            ).set_to_retrived_comment_format()

    def get_comment_by_comment_num(self, commentNum: int):
        all_comments = self.get_comments()
        for comment in all_comments:
            if comment.commentNum == commentNum:
                return comment

    def get_comments_by_writer(self, writerName: str):
        all_comments = self.get_comments()
        commentsByWriter = []
        for comment in all_comments:
            if comment.name == writerName:
                yield comment

    def has_comments_by_writer(self, writerName: str):
        return not(self.get_comments_by_writer(writerName) is [])
