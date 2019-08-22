import json
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from . import orm
from .orm import Word
from .orm import Explain
from .orm import Form
from .orm import Sentence

class Dict:
    database = "localhost"
    _whereCondition=''

    types=["","n.","v.","pron.","adj.","adv.","num.","art.","prep.","conj.","interj.","vt.&vi.","vt.","vi."]

    # 初始化
    def __init__(self,host = "localhost",username = "root",password = "",database = "kewo_dict"):
        self.host = host
        self.username = username
        self.password = password
        self.database = database
        self.engine = None
        self.session = None
        Dict.database = database


    # 连接数据库
    def connectDB(self):
        try:
            self.engine = create_engine(("mysql+pymysql://%s:%s@%s:3306/%s?charset=utf8") % (self.username,self.password,self.host,self.database))
        except:
            print("数据库连接出错")
            return False;
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        return True;

    #关闭数据库
    def closeDB(self):
        if self.session:
            self.session.close()
            self.session = None

    # 存储单词及相关属性,会根据单词无则存
    # name:单词
    # pname:单词原型
    # explains.type:词性 1n 2v3adj
    # explains.content:释义
    # explains.forms.type:变形形式 1过2现3将4复5其他
    # explains.forms.name:词
    # sentencts.content:例句
    # sentencts.content_zh:例句翻译
    # sentencts.source:出处
    # data = [
    #     {
    #         "name": "lie",
    #         "pname": '',
    #         "explains": [
    #             {
    #                 "type": 1,
    #                 "content": "管理",
    #                 "forms": [
    #                     {
    #                         "type": 1,
    #                         "content": "lay",
    #                         "sentencts": [
    #                             {
    #                                 "content": 'dfdfd',
    #                                 "content_zh": "dfdsf",
    #                                 "source": "dfdfds"
    #                             }
    #                         ]
    #                     }
    #                 ],
    #                 "sentencts": [
    #                     {
    #                         "content": 'dfdfd',
    #                         "content_zh": "dfdsf",
    #                         "source": "dfdfds"
    #                     }
    #                 ]
    #             }
    #         ]
    #     }
    # ]
    def word_save(self, data=[]):
        returnData = {}
        returnData['errno'] = 1
        returnData['errmsg'] = "其他错误"

        conn = self.connectDB()
        if not conn:
            self.closeDB()
            returnData['errno'] = 3
            returnData['errmsg'] = "数据库连接异常"
            return returnData
        addobjs = []
        wordpids = []
        for word in data:
            if "name" in word.keys() and word['name']:
                print("处理",word['name'],'单词：')
                tempWordObj = self.session.query(Word).filter_by(name=word['name']).first()

                if not tempWordObj:
                    tempWordObj = Word(name=word['name'])
                    addobjs.append(tempWordObj)
                # 单词释义
                if "explains" in word.keys() and word["explains"]:
                    for explain in word["explains"]:
                        # 判断是否存在释义
                        if "type" in explain.keys() and explain['type']:
                            print("》》释义词性", explain['type'])
                            hasExplain = self.session.query(Explain).filter(Explain.type == explain['type']).filter_by(
                                word_id=tempWordObj.id)
                            tempExplainObj = hasExplain.first()
                            if tempExplainObj and tempWordObj.id:
                                hasExplain.update({"content": explain['content']})
                            else:
                                tempExplainObj = Explain(type=explain['type'],name=self.types[explain['type']], content=explain['content'],word=tempWordObj)
                            if tempWordObj.id:
                                addobjs.append(tempExplainObj)

                            # 词性变换
                            if "forms" in explain.keys() and explain["forms"]:
                                for form in explain["forms"]:
                                    if "content" in form.keys() and form['content']:
                                        print("》》》变形", form['content'])
                                        # 变形单词是否存在
                                        formWordObj = self.session.query(Word).filter_by(name=form['content']).first()
                                        if not formWordObj:
                                            # 新记录
                                            hasInst = False
                                            formWordObj = Word(name=form['content'])
                                            for item in addobjs:
                                                if isinstance(item, Word) and item.name == formWordObj.name:
                                                    hasInst = True
                                                    formWordObj = item
                                                    break

                                            hasInst or addobjs.append(formWordObj)

                                        # 更新关联关系
                                        [formWordObj, tempWordObj] in wordpids or wordpids.append([formWordObj, tempWordObj])
                                        # 变形记录是否存在
                                        tempFormObj = self.session.query(Form).filter(
                                            Form.type == form['type']).filter_by(explain_id=tempExplainObj.id).first()
                                        if tempFormObj:
                                            tempFormObj.content = form['content']
                                            tempFormObj.origin = tempWordObj
                                            tempFormObj.word = formWordObj
                                            tempFormObj.explain = tempExplainObj
                                        else:
                                            tempFormObj = Form(type=form['type'], content=form['content'],
                                                               explain=tempExplainObj, origin=tempWordObj,
                                                               word=formWordObj)

                                        if tempWordObj.id and tempExplainObj.id:
                                            addobjs.append(tempFormObj)

                                        # 例句
                                        if "sentencts" in form.keys() and form["sentencts"]:
                                            for sentenct in form["sentencts"]:
                                                if "content" in sentenct.keys() and sentenct['content']:
                                                    print("》》》》例句", sentenct['content'])
                                                    # 例句是否存在
                                                    tempSentObj = self.session.query(Sentence).filter_by(
                                                        explain_id=tempExplainObj.id).filter_by(
                                                        form_id=tempFormObj.id).first()
                                                    if tempSentObj:
                                                        tempSentObj.content = sentenct['content']
                                                        tempSentObj.content_zh = sentenct['content_zh']
                                                        tempSentObj.source = sentenct['source']
                                                        tempSentObj.word = tempWordObj
                                                        tempSentObj.explain = tempExplainObj
                                                        tempSentObj.form = tempFormObj
                                                    else:
                                                        tempSentObj = Sentence(content_zh=sentenct['content_zh'],
                                                                               content=sentenct['content'],
                                                                               source=sentenct['source'],
                                                                               explain=tempExplainObj,
                                                                               word=tempWordObj,
                                                                               form=tempFormObj)

                                                    if tempWordObj.id and tempExplainObj.id and tempFormObj.id:
                                                        addobjs.append(tempSentObj)

                            # 例句
                            if "sentencts" in explain.keys() and explain["sentencts"]:
                                for sentenct in explain["sentencts"]:
                                    if "content" in sentenct.keys() and sentenct['content']:
                                        print("》》》例句2", sentenct['content'])
                                        # 例句是否存在
                                        tempSentObj = self.session.query(Sentence).filter_by(
                                            explain_id=tempExplainObj.id).first()
                                        if tempSentObj:
                                            tempSentObj.content = sentenct['content']
                                            tempSentObj.content_zh = sentenct['content_zh']
                                            tempSentObj.source = sentenct['source']
                                            tempSentObj.word = tempWordObj
                                            tempSentObj.explain = tempExplainObj
                                        else:
                                            tempSentObj = Sentence(content_zh=sentenct['content_zh'],
                                                                   content=sentenct['content'],
                                                                   source=sentenct['source'], explain=tempExplainObj,
                                                                   word=tempWordObj)

                                        if tempWordObj.id and tempExplainObj.id:
                                            addobjs.append(tempSentObj)

        # 存储数据
        try:
            addobjs and self.session.add_all(addobjs)
            print("数据库commit >>> >>>")
            self.session.commit()
            print("更新单词关联 >>> >>>")
            for tempobj in wordpids:
                print(tempobj[0].id,tempobj[0].name, '>',tempobj[1].id,tempobj[1].name)
                if str(tempobj[0].pid).find(";%s;" % tempobj[1].id)<0:
                    tempobj[0].pid="%s%s;"%(tempobj[0].pid if tempobj[0].pid else ";",tempobj[1].id)
                    self.session.commit()
            print("》》更新完毕《《")
            self.closeDB()
            returnData['errno'] = 0
            returnData['errmsg'] = "成功"
            return returnData
        except SQLAlchemyError as e:
            print(e)
            self.session.rollback()
            self.closeDB()
            returnData['errno'] = 2
            returnData['errmsg'] = "存储异常"
            return returnData
        return returnData

    # 存储单词及相关属性,会根据单词无则存
    # name:单词
    # pname:单词原型
    # explains.type:词性 1n 2v3adj
    # explains.content:释义
    # explains.forms.type:变形形式 1过2现3将4复5其他
    # explains.forms.name:词
    # sentencts.content:例句
    # sentencts.content_zh:例句翻译
    # sentencts.source:出处
    # data = [
    #     {
    #         "name": "lie",
    #         "pname": '',
    #         "explains": [
    #             {
    #                 "type": 1,
    #                 "content": "管理",
    #                 "forms": [
    #                     {
    #                         "type": 1,
    #                         "content": "lay",
    #                         "sentencts": [
    #                             {
    #                                 "content": 'dfdfd',
    #                                 "content_zh": "dfdsf",
    #                                 "source": "dfdfds"
    #                             }
    #                         ]
    #                     }
    #                 ],
    #                 "sentencts": [
    #                     {
    #                         "content": 'dfdfd',
    #                         "content_zh": "dfdsf",
    #                         "source": "dfdfds"
    #                     }
    #                 ]
    #             }
    #         ]
    #     }
    # ]
    def word_save_force(self,data=[]):
        returnData = {}
        returnData['errno'] = 1
        returnData['errmsg'] = "其他错误"

        conn = self.connectDB()
        if not conn:
            self.closeDB()
            returnData['errno'] = 3
            returnData['errmsg'] = "数据库连接异常"
            return returnData
        addobjs=[]
        wordpids=[]
        for word in data:
            if "name" in word.keys() and word['name']:
                print("处理", word['name'], '单词：')
                tempWordObj = self.session.query(Word).filter_by(name=word['name']).first()
                if tempWordObj:
                    self.session.delete(tempWordObj)
                    self.session.execute("update kewo_words set%s pid=REPLACE(pid,';%s;',';')"%('',tempWordObj.id))
                tempWordObj = Word(name=word['name'])
                addobjs.append(tempWordObj)
                # 单词释义
                if "explains" in word.keys() and word["explains"]:
                    for explain in word["explains"]:
                        # 判断是否存在释义
                        if "type" in explain.keys() and explain['type']:
                            print("》》释义词性", explain['type'])
                            hasExplain = self.session.query(Explain).filter(Explain.type == explain['type']).filter_by(word_id=tempWordObj.id).first()
                            tempExplainObj = hasExplain
                            if hasExplain:
                                self.session.delete(hasExplain)

                            tempExplainObj = Explain(type=explain['type'], content=explain['content'],word=tempWordObj)

                            # 词性变换
                            if "forms" in explain.keys() and explain["forms"]:
                                for form in explain["forms"]:
                                    if "content" in form.keys() and form['content']:
                                        print("》》》变形", form['content'])
                                        # 变形单词是否存在
                                        formWordObj = self.session.query(Word).filter_by(name=form['content']).first()
                                        if not formWordObj:
                                            # 新记录
                                            hasInst = False
                                            formWordObj = Word(name=form['content'])
                                            for item in addobjs:
                                                if isinstance(item, Word) and item.name == formWordObj.name:
                                                    hasInst = True
                                                    formWordObj = item
                                                    break

                                            hasInst or addobjs.append(formWordObj)
                                        # 更新关联关系
                                        [formWordObj, tempWordObj] in wordpids or wordpids.append([formWordObj, tempWordObj])
                                        # 变形记录是否存在
                                        tempFormObj = self.session.query(Form).filter(Form.type == form['type']).filter_by(explain_id=tempExplainObj.id).first()
                                        if tempFormObj:
                                            self.session.delete(tempFormObj)

                                        tempFormObj = Form(type=form['type'],content=form['content'],explain=tempExplainObj,origin=tempWordObj,word=formWordObj)

                                        # 例句
                                        if "sentencts" in form.keys() and form["sentencts"]:
                                            for sentenct in form["sentencts"]:
                                                if "content" in sentenct.keys() and sentenct['content']:
                                                    print("》》》》例句2", sentenct['content'])
                                                    # 例句是否存在
                                                    tempSentObj = self.session.query(Sentence).filter_by(content=sentenct['content']).filter_by(explain_id=tempExplainObj.id).filter_by(form_id=tempFormObj.id).first()
                                                    if tempSentObj:
                                                        self.session.delete(tempSentObj)
                                                    tempSentObj = Sentence(content_zh=sentenct['content_zh'],
                                                                               content=sentenct['content'],
                                                                               source=sentenct['source'],
                                                                               explain=tempExplainObj,
                                                                               word=tempWordObj,
                                                                               form=tempFormObj)

                            # 例句
                            if "sentencts" in explain.keys() and explain["sentencts"]:
                                for sentenct in explain["sentencts"]:
                                    if "content" in sentenct.keys() and sentenct['content']:
                                        print("》》》例句2", sentenct['content'])
                                        # 例句是否存在
                                        tempSentObj = self.session.query(Sentence).filter_by(content=sentenct['content']).filter_by(
                                            explain_id=tempExplainObj.id).first()
                                        if tempSentObj:
                                            self.session.delete(tempSentObj)
                                        tempSentObj = Sentence(content_zh=sentenct['content_zh'],
                                                                   content=sentenct['content'],
                                                                   source=sentenct['source'], explain=tempExplainObj,
                                                                   word=tempWordObj)

        # 存储数据
        try:
            addobjs and self.session.add_all(addobjs)
            print("数据库commit >>> >>>")
            self.session.commit()
            print("更新单词关联 >>> >>>")
            for tempobj in wordpids:
                print(tempobj[0].id, tempobj[0].name, '>', tempobj[1].id, tempobj[1].name)
                if str(tempobj[0].pid).find(";%s;" % tempobj[1].id)<0:
                    tempobj[0].pid="%s%s;"%(tempobj[0].pid if tempobj[0].pid else ";",tempobj[1].id)
                    self.session.commit()
            print("》》更新完毕《《")
            self.closeDB()
            returnData['errno'] = 0
            returnData['errmsg'] = "成功"
            return returnData
        except:
            self.session.rollback()
            self.closeDB()
            returnData['errno'] = 2
            returnData['errmsg'] = "存储异常"
            return returnData
        return returnData

    # 删除单词
    # data 单词
    def word_del(self,data=None):
        returnData = {}
        returnData['errno'] = 1
        returnData['errmsg'] = "其他错误"
        if not data:
            returnData['errno'] = 2
            returnData['errmsg'] = "无参数"
            return returnData

        conn = self.connectDB()
        if not conn:
            self.closeDB()
            returnData['errno'] = 3
            returnData['errmsg'] = "数据库连接异常"
            return returnData
        self.session.query(Word).filter(Word.name==data).delete(synchronize_session=False)
        self.session.commit()
        returnData['errno'] = 0
        returnData['errmsg'] = "成功"

        self.closeDB()
        return returnData

    # 删除释义
    # data 单词 type 释义类型
    def explain_del(self, data=None,type=[]):
        returnData = {}
        returnData['errno'] = 1
        returnData['errmsg'] = "其他错误"
        if not data:
            returnData['errno'] = 2
            returnData['errmsg'] = "无参数"
            return returnData

        conn = self.connectDB()
        if not conn:
            self.closeDB()
            returnData['errno'] = 3
            returnData['errmsg'] = "数据库连接异常"
            return returnData

        obj = self.session.query(Word).filter(Word.name == data).first()
        if obj:
            exObj = self.session.query(Explain).filter(Explain.word_id == obj.id)
            if type:
                exObj = exObj.filter(Explain.type.in_(type))
            exObj.delete(synchronize_session=False)
            self.session.commit()
            returnData['errno'] = 0
            returnData['errmsg'] = "成功"
            return returnData
        else:
            returnData['errno'] = 4
            returnData['errmsg'] = "无单词"
            return returnData
        self.closeDB()
        return returnData

    # 删除变形
    # data 单词 type 变形类型
    def form_del(self, data=None,type=[]):
        returnData = {}
        returnData['errno'] = 1
        returnData['errmsg'] = "其他错误"
        if not data:
            returnData['errno'] = 2
            returnData['errmsg'] = "无参数"
            return returnData

        conn = self.connectDB()
        if not conn:
            self.closeDB()
            returnData['errno'] = 3
            returnData['errmsg'] = "数据库连接异常"
            return returnData

        # 查单词
        obj = self.session.query(Word).filter(Word.name == data).first()
        print(obj.id)
        if obj:
            formObj = self.session.query(Form).filter(Form.origin_id == obj.id)
            if len(type)>0:
                formObj = formObj.filter(Form.type.in_(type))
            formObj.delete(synchronize_session=False)
            self.session.commit()
            returnData['errno'] = 0
            returnData['errmsg'] = "成功"
            return returnData
        else:
            returnData['errno'] = 4
            returnData['errmsg'] = "无单词"
            return returnData
        self.closeDB()
        return returnData


    # 删除例句
    # data 单词 type 释义类型
    def sentence_del(self, data=None,type=[]):
        returnData={}
        returnData['errno'] = 1
        returnData['errmsg'] = "其他错误"
        if not data:
            returnData['errno'] = 2
            returnData['errmsg'] = "无参数"
            return returnData

        conn = self.connectDB()
        if not conn:
            self.closeDB()
            returnData['errno'] =3
            returnData['errmsg'] = "数据库连接异常"
            return returnData

        # 查单词
        obj = self.session.query(Word).filter(Word.name == data).one_or_none()
        if obj:
            sentenceObj = self.session.query(Sentence).filter(Sentence.word_id == obj.id)
            if type:
                sentenceObj = sentenceObj.filter(Sentence.explain_id.in_(self.session.query(Explain.id).filter(Explain.word_id==obj.id).filter(Explain.type.in_(type))))

            sentenceObj.delete(synchronize_session=False)
            self.session.commit()
            returnData['errno'] = 0
            returnData['errmsg'] = "成功"
            return returnData
        else:
            returnData['errno'] = 4
            returnData['errmsg'] = "无单词"
            return returnData
        self.closeDB()
        return returnData

    # 创建数据库
    def init_db(self):
        engine = create_engine("mysql+pymysql://root:@localhost:3306/kewo_dict?charset=utf8",
                               max_overflow = 0,  # 超过连接池大小外最多创建的连接
                               pool_size = 5,  # 连接池大小
                               pool_timeout = 30,  # 池中没有线程最多等待的时间，否则报错
                               pool_recycle = -1  # 多久之后对线程池中的线程进行一次连接的回收（重置）
                            )
        orm.Base.metadata.create_all(engine)

    # 查询单词 infoLevel 0单词 1释义 2变形 3例句
    def word(self,name=None,infoLevel=0):
        returnData = {}
        returnData['errno'] = 1
        returnData['errmsg'] = "暂无数据"

        if not name:
            returnData['errno'] = 2
            returnData['errmsg'] = "缺少单词"
            return returnData

        conn = self.connectDB()
        if not conn:
            self.closeDB()
            returnData['errno'] = 3
            returnData['errmsg'] = "数据库连接异常"
            return returnData

        obj = self.session.query(Word).filter(Word.name == name).one_or_none()
        if obj:
            data = self.format_word(obj,infoLevel)

            if data:
                returnData['errno'] = 0
                returnData['errmsg'] = "成功"
                returnData['datas'] = data
            else:
                returnData['errno'] = 4
                returnData['errmsg'] = "格式化异常"
            return returnData

        return returnData

    def format_word(self,obj,infoLevel=0):
        returndata=None

        if obj:
            data = self.format_orm(obj)

            if infoLevel > 0:
                data['explains'] = []
                for i in range(0, len(obj.explains)):
                    temp = {}
                    temp = self.format_orm(obj.explains[i], 'explain')
                    if infoLevel > 1:
                        temp["forms"] = self.format_orm(obj.explains[i].forms, 'form')
                    if infoLevel > 2:
                        temp["sentences"] = self.format_orm(obj.explains[i].sentences, 'sentence')
                    data['explains'].append(temp)
            returndata = data
        return returndata

    def format_orm(self,data,type="word"):
        returndata=None

        if data:
            if isinstance(data,list):
                returndata = []
                for item in data:
                    temp = self.format_orm_item(item,type)
                    returndata.append(temp)
            else:
                returndata = self.format_orm_item(data, type)
        return returndata

    def format_orm_item(self, data, type="word"):
        returndata = ''
        if data:
            switch = {
                "word":lambda data:{'id':data.id,'name':data.name},
                "explain": lambda data: {'name': data.name,'content':data.content},
                "form": lambda data: {'content': data.content,'type':data.type},
                "sentence": lambda data: {'content': data.content,'content_zh': data.content_zh, 'source': data.source}
            }

            returndata = switch[type](data)

        return returndata

    # 查询单词 infoLevel 0单词 1释义 2变形 3例句
    def word_relate(self,name=None,infoLevel=0):
        returnData = {}
        returnData['errno'] = 1
        returnData['errmsg'] = "暂无数据"

        if not name:
            returnData['errno'] = 2
            returnData['errmsg'] = "缺少单词"
            return returnData

        conn = self.connectDB()
        if not conn:
            self.closeDB()
            returnData['errno'] = 3
            returnData['errmsg'] = "数据库连接异常"
            return returnData

        obj = self.session.query(Word).filter(Word.name == name).one_or_none()
        if obj:
            data={}
            data['word']= self.format_word(obj,infoLevel)
            # 查询相关联的单词
            prelate=[]
            if obj.forms:
                temprelate = []
                prelate_item = {}
                for item in obj.forms:
                    tempform={}
                    tempform['word'] = self.format_word(item.word,infoLevel)
                    tempform['type'] =item.type
                    temprelate.append(tempform)
                prelate_item['word'] = data['word'].copy()
                prelate_item['relates'] = temprelate
                prelate.append(prelate_item)
            if obj.words:
                for item in obj.words:
                    prelate_item = {}
                    prelate_item['word'] = self.format_word(item.origin, infoLevel)
                    temprelate = []
                    itemword = self.format_word(item.word, infoLevel)
                    for sitem in item.origin.forms:
                        tempform = {}
                        tempform['word'] = itemword
                        tempform['type'] = sitem.type
                        temprelate.append(tempform)
                    prelate_item['relates'] = temprelate
                    prelate.append(prelate_item)
            data['relates'] = prelate
            returnData['errno'] = 0
            returnData['errmsg'] = "成功"
            returnData['datas'] = data
            return returnData

        return returnData

    def test(self,data):
        print(data)
        lists = []
        aitem = Explain(content="dfd")
        listsitem = Word(name="dfdf")

        listsitem2 = Word(name="dfdf")
        lists.append(aitem)
        lists.append(listsitem)
        topli = [lists]
        print(topli,lists in topli,[aitem,listsitem] in topli)

        # hasInst=False
        # for item in lists:
        #     print(item)
        #     if isinstance(item,Word) and item.name==listsitem2.name:
        #         print(123)
        #         hasInst = True
        #         break
        #
        # hasInst or lists.append(listsitem2)
        #
        #
        # print(lists,listsitem2 in lists)