'''
超导移动端API大全
cjdg_api类
url_type 表示接口所在的服务。
'''
import json
import requests

__version__ = '1.0.0'

class cjdg_api(object):
    """docstring for cjdg_api"""

    def __init__(self, acc, pwd, url_type="bms"):
        super(cjdg_api, self).__init__()
        self.acc = acc
        self.pwd = pwd
        url_list = {
            "bms": "http://bms.microc.cn/shopguide/api/",
            "pre": "http://pre.xxynet.com/shopguide/api/",
            "it": "http://it.xxynet.com/shopguide/api/",
            "test": "http://test.xxynet.com/shopguide/api/",
            "allstar": "http://client.supshop.cn/allstar/api/",
        }
        self.url = url_list[url_type]
        self.accessToken = self.request_accesstoken()

    def __str__(self):
        return self.accessToken

    def api_request(self, url, data=None, method="GET"):
        if method == "GET":
            resp = requests.get(url, params=data)
        elif method == "POST":
            resp = requests.post(url, data)
        else:
            raise ValueError("HTTP请求方法不正确。")

        if resp.status_code == 200:
            return resp.json()

    def getTagList(self, **data):
        url = self.url + "bbs/getTagList"
        data["accessToken"] = self.accessToken
        return self.api_request(url, data)

    def activityAddTopic(self, **data):
        url = self.url + "activity/addTopic"
        data["accessToken"] = self.accessToken
        print(data)
        return self.api_request(url, data)

    def getBookList(self):
        # 书本列表
        url = self.url + "emba/getBookList"
        data = {}
        data["accessToken"] = self.accessToken
        return self.api_request(url, data)

    def getBookDir(self, book_id):
        # 书的目录结构
        url = self.url + "emba/getBookDir"
        data = {}
        data["accessToken"] = self.accessToken
        data["book_id"] = book_id
        return self.api_request(url, data)

    def getCourseList(self, interface_type=3):
        # 书的目录结构
        url = self.url + "emba/getCourseList"
        data = {}
        data["accessToken"] = self.accessToken
        data["interface_type"] = interface_type
        return self.api_request(url, data)

    def request_accesstoken(self):
        # 请求accesstooke函数
        url = self.url + "auth/logon"
        data = {}
        data["loginName"] = self.acc
        data["password"] = self.pwd
        data["version"] = "1"
        # print(url,data)
        accessToken = self.api_request(url, data).get("accessToken", 0)
        if accessToken != 0:
            # print(accessToken)
            self.accessToken = accessToken
            return accessToken
        else:
            print("用户名密码错误。")
            return("用户名密码错误。")
            # exit()

    def getSingin(self):
        url = self.url + "game/addNewUserSignin"
        data = {}
        data["accessToken"] = self.accessToken
        return self.api_request(url, data)

    def getUser(self):
        url = self.url + "game/getUser"
        data = {}
        data["accessToken"] = self.accessToken
        return self.api_request(url, data)

    def addUserSignin(self):
        url = self.url + "game/addUserSignin"
        data = {}
        data["accessToken"] = self.accessToken
        return self.api_request(url, data)

    def activateEnterpriseAcc(self, cdkey):
        # 激活
        url = self.url + "game/activateEnterpriseAcc"
        print(url)
        data = {}
        data["accessToken"] = self.accessToken
        data["cdkey"] = cdkey
        # print(data)
        return self.api_request(url, data)

    def addBbsForumAndTag(self, imgs="", context=""):
        url = self.url + "v2/bbs/addBbsForumAndTag"
        data = {}
        data["accessToken"] = self.accessToken
        data["imgs"] = imgs
        data["context"] = context
        return self.api_request(url, data)

    def getActivityList(self):
        url = self.url + "bbs/getActivityList"
        data = {}
        data["accessToken"] = self.accessToken
        # data["imgs"]=imgs
        # data["context"]=context
        return self.api_request(url, data)

    def get_goods_list(self, **data):
        url = self.url + "fab/goods/list"
        data["accessToken"] = self.accessToken
        return self.api_request(url, data)

    def set_goods_edit(self, **data):
        url = self.url + "fab/goods/edit"
        data["accessToken"] = self.accessToken
        return self.api_request(url, data)

    def getArticleById(self, **data):
        url = self.url + "contmgn/getArticleById"
        data["accessToken"] = self.accessToken
        # data["articleId"] = 93927
        return self.api_request(url, data)

    def addComment(self, **data):
        url = self.url + "contmgn/addComment"
        data["accessToken"] = self.accessToken
        # data["articleId"] = 93927
        # data["content"] = 好
        data["stren"] = 0
        # print(data)
        return self.api_request(url, data)

    def addPraiseNum(self, **data):
        url = self.url + "contmgn/addPraiseNum"
        data["accessToken"] = self.accessToken
        # data["articleId"] = 93927
        # print(data)
        return self.api_request(url, data)

    def activity_addTopic(self, **data):
        url = self.url + "activity/addTopic"
        data["accessToken"] = self.accessToken
        # data["activityId"] = 93927
        # data["content"] = 93927
        # data["topicPic"] = 93927
        # print(data)
        return self.api_request(url, data)

    def globalSearchActivity(self, keyWord):
        # 全局搜索活动
        url = self.url + "globalSearchActivity"
        data = {}
        data["accessToken"] = self.accessToken
        data["keyWord"] = keyWord
        data["page"] = 1
        data["type"] = "activity"
        return self.api_request(url, data)

    def globalSearchArticle(self, keyWord):
        # globalSearchArticle
        url = self.url + "globalSearchArticle"
        data = {}
        data["accessToken"] = self.accessToken
        data["keyWord"] = keyWord
        data["page"] = 1
        data["type"] = "activity"
        return self.api_request(url, data)

    def getCommentListByArticleId(self, articleId, page):
        # 全局搜索活动
        # http://bms.xxynet.com/shopguide/api/
        # accessToken:bd1af3174cbedb6d539f9d3625418589_xtep
        # articleId:118239
        # page:1
        # rows:20
        url = self.url + "contmgn/getCommentListByArticleId"
        data = {}
        data["accessToken"] = self.accessToken
        data["articleId"] = articleId
        data["page"] = page
        data["rows"] = 20
        return self.api_request(url, data)

    def addReplyPraise(self, targetId, articleId):
        # 全局搜索活动
        # http://bms.xxynet.com/shopguide/api/contmgn/addReplyPraise
        # accessToken	3ea7b9e9dca85f8e1d3ebf93e9e0137f_xtep
        # favourToType	3
        # favourType	2
        # targetId	33330192
        # targetParentId	117694
        url = self.url + "contmgn/addReplyPraise"
        data = {}
        data["accessToken"] = self.accessToken
        data["favourToType"] = 3
        data["favourType"] = 2
        data["targetId"] = targetId
        data["targetParentId"] = articleId
        return self.api_request(url, data)

    def activity_getTopicList(self, activityId, page):
        # 活动楼层信息
        url = self.url + "activity/getTopicList"
        data = {}
        data["accessToken"] = self.accessToken
        data["activityId"] = activityId
        data["onlyShowImg"] = 0
        data["order"] = 1
        data["page"] = page
        data["rows"] = 1
        return self.api_request(url, data)

    def activityLikeOper(self, activityId, floor, replyId):
        # 活动点赞
        url = self.url + "activity/activityLikeOper"
        data = {}
        data["accessToken"] = self.accessToken
        data["activityId"] = activityId
        data["floor"] = floor
        data["replyId"] = replyId
        return self.api_request(url, data)

    def updateUserPassword(self, oldPassword, newPassword):
        # 书本列表
        url = self.url + "auth/updateUserPassword"
        data = {}
        data["accessToken"] = self.accessToken
        data["oldPassword"] = oldPassword
        data["newPassword"] = newPassword
        return self.api_request(url, data)

    def addOrDelBbsFavour(self, favourRelId):
        url = self.url + "bbs/addOrDelBbsFavour"
        data = {}
        data["accessToken"] = self.accessToken
        data["editType"] = 1
        data["favourId"] = 0
        data["favourRelId"] = favourRelId
        data["favourToType"] = 1
        data["favourType"] = 1
        data["relId"] = favourRelId
        return self.api_request(url, data, method="POST")

    def getBbsForumListAndTag(self):
        url = self.url + "v2/bbs/getBbsForumListAndTag"
        data = {}
        data["accessToken"] = self.accessToken
        data["interactionType"] = 0
        data["page"] = 1
        data["rows"] = 100
        data["version"] = 1
        return self.api_request(url, data)


def lecture_getVideos(accessToken):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"

    }
    url = "http://client.supshop.cn/allstar/api/" + "lecture/getVideos"
    data = {
        "tagids": 316,
        "order": 1,
        "accessToken": accessToken,
        "pageSize": 100,
        "nowPage": 1,
    }
    while 1:
        try:
            result = requests.get(url, params=data, headers=headers)
            break
        except Exception as e:
            print(e)
            continue
    return json.loads(result.content.decode("utf-8"))


def lecture_addUserLike(accessToken, evaType, c_id):
    # 书本列表
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"

    }
    url = "http://client.supshop.cn/allstar/api/" + "lecture/addUserLike"
    data = {}
    data["accessToken"] = accessToken
    data["evaType"] = evaType
    data["id"] = c_id
    while 1:
        try:
            result = requests.post(url, params=data, headers=headers)
            break
        except Exception as e:
            print(e)
            continue
    return json.loads(result.content.decode("utf-8"))


def lecture_addComment(accessToken, cont, c_id):
    # 书本列表
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    url = "http://client.supshop.cn/allstar/api/" + "lecture/addComment"
    param = {}
    param["accessToken"] = accessToken
    data = {}
    data["contentId"] = c_id
    data["cont"] = cont
    print(data)
    while 1:
        try:
            result = requests.post(url, data=json.dumps(
                data), params=param, headers=headers)
            break
        except Exception as e:
            print(e)
            continue
    return json.loads(result.content.decode("utf-8"))