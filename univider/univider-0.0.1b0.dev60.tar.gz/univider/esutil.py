# -*- coding: UTF-8 -*-
import json
import hashlib
from elasticsearch import Elasticsearch
from settings import es_host
es = Elasticsearch(es_host)

def md5(str):
    m = hashlib.md5()
    m.update(str)
    return m.hexdigest()

def save_yuqing_article(title="", mp_name="", content="", post_date="", link="", html="", mp_code="", mp_desc="", copyright_logo="", article_author="", crawl_time="",msg_cdn_id='',hd_head_img='',url='',user_name=''):

    data = {}
    data['title'] = title
    data['mp_name'] = mp_name
    data['content'] = content
    data['post_date'] = post_date
    data['link'] = link
    data['html'] = html
    data['mp_code'] = mp_code
    data['mp_desc'] = mp_desc
    data['copyright_logo'] = copyright_logo
    data['article_author'] = article_author
    data['msg_cdn_id'] = msg_cdn_id
    data['hd_head_img'] = hd_head_img
    data['url'] = url
    data['user_name'] = user_name
    data['crawl_time'] = crawl_time

    index = "yuqing_index"
    doc_type = "article"
    body = json.dumps(data, ensure_ascii=False)
    id = md5(title+mp_name)
    # print body

    es.index(index=index, doc_type=doc_type, body=body, id=id)



def save_tianyan_qiye(company='',ein='',gszc='',zzjgdm='',yy_date='',past_Date='',crawl_time=''):
    data_user = {}
    data_user['company'] = company
    data_user['ein'] = ein
    data_user['gszc'] = gszc
    data_user['zzjgdm'] = zzjgdm
    data_user['yy_date'] = yy_date
    data_user['past_Date'] = past_Date
    data_user['crawl_time'] = crawl_time

    index = "tianyan_qiye"
    doc_type = "tianyan_qiye_type"
    body = json.dumps(data_user, ensure_ascii=False)
    id = md5(company+ein)
    # print body

    es.index(index=index, doc_type=doc_type, body=body, id=id)



def save_user(bill_no='',start_time='',end_time='',content_id='',uri='',lat='',lon='',crawl_time=''):
    data_user = {}
    data_user['bill_no'] = bill_no
    data_user['start_time'] = start_time
    data_user['end_time'] = end_time
    data_user['content_id'] = content_id
    data_user['uri'] = uri
    data_user['lat'] = lat
    data_user['lon'] = lon
    data_user['crawl_time'] = crawl_time

    index = "qtt_user"
    doc_type = "qtt_user_type"
    body = json.dumps(data_user, ensure_ascii=False)
    id = md5(bill_no+content_id+start_time)
    # print body

    es.index(index=index, doc_type=doc_type, body=body, id=id)


def save_qtt_content(content_id='',content_type='',title='',zhuti='',uri='',post_time='',author_id='',nickname='',is_origin='',content='',comment_json='',html='',crawl_time=''):
    data_content = {}
    data_content['content_id'] = content_id
    data_content['content_type'] = content_type
    data_content['title'] = title
    data_content['zhuti'] = zhuti
    data_content['uri'] = uri
    data_content['post_time'] = post_time
    data_content['author_id'] = author_id
    data_content['nickname'] = nickname
    data_content['is_origin'] = is_origin
    data_content['content'] = content
    data_content['comment_json'] = comment_json
    data_content['html'] = html
    data_content['crawl_time'] = crawl_time

    index = "qtt_content"
    doc_type = "qtt_content_type"
    body = json.dumps(data_content, ensure_ascii=False)
    id = md5(content_id)
    # print body

    es.index(index=index, doc_type=doc_type, body=body, id=id)


def save_qtt_comment(content_id='',nickname='',comment_id='',comment='',post_time='',like_num='',crawl_time=''):
    data_comment = {}
    data_comment['content_id'] = content_id
    data_comment['nickname'] = nickname
    data_comment['comment_id'] = comment_id
    data_comment['comment'] = comment
    data_comment['post_time'] = post_time
    data_comment['like_num'] = like_num
    data_comment['crawl_time'] = crawl_time

    index = "qtt_comment"
    doc_type = "qtt_comment_type"
    body = json.dumps(data_comment, ensure_ascii=False)
    id = md5(comment_id)
    # print body

    es.index(index=index, doc_type=doc_type, body=body, id=id)


if __name__ == '__main__':
    save_yuqing_article(
        title="title1"
        , mp_name="mp_name"
        , content="content"
        , post_date="2015-12-31"
        , link="http://www.baidu.com/xxxxx"
        , url = "http://www.baidu.com/xxxxx"
        , html="html"
        , mp_code="haha"
        , mp_desc="mp_desc"
        , copyright_logo="copyright_logo"
        , article_author="article_author"
        , msg_cdn_id = "msg_cdn_id"
        , hd_head_img = "hd_head_img"
        , user_name="user_name"
        , crawl_time="2017-12-31 12:31:21"
    )
    # 趣头条文章
    save_qtt_content(
        content_id='',  # 文章id
        title='',  # 标题
        zhuti='',  # 主题分类
        uri='',  # uri
        post_time='',  # 发布时间
        author_id='',  # 发布作者id
        nickname='',  # 发布作者
        is_origin='',  # 是否原创
        content='',  # 文章内容
        comment_json='',  # 评论(json格式)
        html='',  # 网页源码
        crawl_time=''  # 爬取时间
    )
    # 趣头条文章评论
    save_qtt_comment(
        content_id='',  # 文章id
        nickname='',  # 评论者昵称
        comment_id='',  # 评论id
        comment='',  # 评论内容
        post_time='',  # 评论时间
        like_num='',  # 评论点赞数
        crawl_time=''  # 爬取时间
    )
    # 用户信息
    save_user(
        bill_no='',  # 号码
        start_time='',
        end_time='',
        content_id='',  # 文章id
        uri='',  # uri
        lat='',  # 经纬度
        lon='',  # 经纬度
        crawl_time=''  # 爬取时间
    )
