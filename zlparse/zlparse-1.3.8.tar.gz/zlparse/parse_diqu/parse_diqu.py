# encoding=utf-8
import json
import os
import re
from bs4 import BeautifulSoup
import jieba
import pandas as pd
from sqlalchemy import create_engine


# 连接数据库
def getpage_herf_ggstart_time(quyu):
    arr = quyu.split('*')
    db, schema = arr[0], arr[1]
    engine = create_engine('postgresql+psycopg2://postgres:since2015@192.168.3.171/%s' % (db))
    data_gg_html = pd.read_sql_table(table_name='gg_html', con=engine, schema=schema, index_col=None, coerce_float=True,
                                     parse_dates=None, columns=None, chunksize=None)
    df = data_gg_html[['href', 'page']]
    return df


# 读入数据库
def write_to_table(df, table_name, quyu, if_exists='replace'):
    import io
    import pandas as pd
    from sqlalchemy import create_engine
    arr = quyu.split('*')
    db, schema = arr[0], arr[1]
    db_engine = create_engine('postgresql+psycopg2://postgres:since2015@192.168.3.171/%s' % db)
    string_data_io = io.StringIO()
    df.to_csv(string_data_io, sep='|', index=False)
    pd_sql_engine = pd.io.sql.pandasSQL_builder(db_engine)
    table = pd.io.sql.SQLTable(table_name, pd_sql_engine, frame=df, index=False, if_exists=if_exists, schema=schema)
    table.create()
    string_data_io.seek(0)
    string_data_io.readline()  # remove header
    with db_engine.connect() as connection:
        with connection.connection.cursor() as cursor:
            copy_cmd = "COPY %s.%s FROM STDIN HEADER DELIMITER '|' CSV" % (schema, table_name)
            cursor.copy_expert(copy_cmd, string_data_io)
        connection.connection.commit()


def wrap(cls, *args, **kwargs):
    def inner(*args, **kwargs):
        p_diqu = cls()
        quyu = args[0]
        page = args[1]
        res = p_diqu.parse_diqu(quyu, page)
        return res

    return inner


def singleton(cls, *args, **kwargs):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@wrap
@singleton
class parseDiqu(object):
    def __init__(self):
        self.__jieba_init__()
        # self.haimei = []

    def __jieba_init__(self):

        json_path = os.path.join(os.path.dirname(__file__), 'list.json')
        with open(json_path, encoding='utf-8') as f:
            self.xzqh_key_word_dict_list = json.load(f)

        json_path2 = os.path.join(os.path.dirname(__file__), 'list2.json')
        with open(json_path2, encoding='utf-8') as f:
            self.xzqh_key_word_dict_list2 = json.load(f)

        self.data = pd.DataFrame.from_dict(self.xzqh_key_word_dict_list, orient='index')
        self.data.reset_index(inplace=True)
        self.data.columns = ['code', 'word']
        self.new_diqu_list = self.data['word'].tolist()
        jieba.load_userdict(self.new_diqu_list)
        # 设置高词频：dict.txt中的每一行都设置一下
        for line in self.new_diqu_list:
            line = line.strip()
            jieba.suggest_freq(line, tune=True)
        self.data['code'] = self.data['code'].astype('str')
        # shape[0] 首个
        # print(self.data.shape  )shape  数据框格式
        for i in list(range(self.data.shape[0])):
            # 去掉省的后四位，市的后两位。
            if len(self.data['code'][i]) > 2:
                if re.findall('[0-9][0-9][0]{4}', self.data['code'][i]):
                    self.data['code'][i] = self.data['code'][i][:2]
                else:
                    self.data['code'][i] = self.data['code'][i][:4]

    def t_page(self, page):
        if page is None:
            return []
        self.soup = BeautifulSoup(page, 'lxml')
        tmp = self.soup.find('style')
        if tmp is not None:
            tmp.clear()
        tmp = self.soup.find('script')
        if tmp is not None:
            tmp.clear()
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', self.soup.text.strip())
        return txt

    def count_diqu(self, txt_list):
        object_list = []
        if self.soup.find('h1') :
            txt1 = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', self.soup.find('h1').text.strip())

            for word in jieba.cut(txt1, cut_all=False):
                if word in self.new_diqu_list:
                    object_list.append(self.data['code'][self.data['word'] == word].tolist()[0])
            if object_list == []:
                if re.findall("(?:招标人|代理机构|交货地点[:：]{0,1})(.{0,20})", txt_list):
                    txt2 = re.findall("(?:招标人|代理机构|交货地点[:：]{0,1})(.{0,20})", txt_list)[0]
                    for word in jieba.cut(txt2, cut_all=False):
                        if word in self.new_diqu_list:
                            object_list.append(self.data['code'][self.data['word'] == word].tolist()[0])
                    if object_list == []:
                        for word in jieba.cut(txt_list, cut_all=False):
                            if word in self.new_diqu_list:
                                object_list.append(self.data['code'][self.data['word'] == word].tolist()[0])
                else:
                    for word in jieba.cut(txt_list, cut_all=False):
                        if word in self.new_diqu_list:
                            object_list.append(self.data['code'][self.data['word'] == word].tolist()[0])

        elif self.soup.find(string=re.compile('工程|项目')):
            txt1 = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', self.soup.find(string=re.compile('工程|项目')).strip())
            for word in jieba.cut(txt1, cut_all=False):
                if word in self.new_diqu_list:
                    object_list.append(self.data['code'][self.data['word'] == word].tolist()[0])

                    print(self.data['code'][self.data['word'] == word].tolist()[0])

            if object_list == []:
                if re.findall("(?:招标人|代理机构|交货地点[:：]{0,1})(.{0,20})", txt_list):
                    txt2 = re.findall("(?:招标人|代理机构|交货地点[:：]{0,1})(.{0,20})", txt_list)[0]
                    for word in jieba.cut(txt2, cut_all=False):
                        if word in self.new_diqu_list:
                            object_list.append(self.data['code'][self.data['word'] == word].tolist()[0])
                    if object_list == []:
                        for word in jieba.cut(txt_list, cut_all=False):
                            if word in self.new_diqu_list:
                                object_list.append(self.data['code'][self.data['word'] == word].tolist()[0])
                else:
                    for word in jieba.cut(txt_list, cut_all=False):
                        if word in self.new_diqu_list:
                            object_list.append(self.data['code'][self.data['word'] == word].tolist()[0])

        else:
            if re.findall("(?:招标人|代理机构|交货地点[:：]{0,1})(.{0,20})", txt_list):
                txt2 = re.findall("(?:招标人|代理机构|交货地点[:：]{0,1})(.{0,20})", txt_list)[0]
                for word in jieba.cut(txt2, cut_all=False):
                    if word in self.new_diqu_list:
                        object_list.append(self.data['code'][self.data['word'] == word].tolist()[0])
                if object_list == []:
                    for word in jieba.cut(txt_list, cut_all=False):
                        if word in self.new_diqu_list:
                            object_list.append(self.data['code'][self.data['word'] == word].tolist()[0])
            else:
                for word in jieba.cut(txt_list, cut_all=False):
                    if word in self.new_diqu_list:
                        object_list.append(self.data['code'][self.data['word'] == word].tolist()[0])
        print(object_list)
        if object_list != []:
            count = {}
            dit = {}
            for value, key in enumerate(object_list):
                if dit.get(key, 0):
                    count[key] = count[key] + 1
                else:
                    count[key] = 1
                    dit[key] = value + 1
            cnt_data = pd.DataFrame([count])
            cnt_data = pd.melt(cnt_data)
            cnt_data.columns = ['code', 'cnt']
            rank_data = pd.DataFrame([dit])
            rank_data = pd.melt(rank_data)
            rank_data.columns = ['code', 'rank']
            df_final = cnt_data.merge(rank_data, left_on='code', right_on='code')
            df_final['length'] = df_final['code'].map(lambda x: len(x))
            df_final.sort_values(by=['rank'], ascending=True, inplace=True)
            df_final.sort_values(by=['cnt'], ascending=False, inplace=True)
            df_final.reset_index(drop=True, inplace=True)
            if df_final.shape[0] > 1:
                if re.findall('[0-9]{2}', str([df_final['code'][0]]))[0] == re.findall('[0-9]{2}', str([df_final['code'][1]]))[0]:
                    if df_final['length'][0] < df_final['length'][1]:
                        return df_final['code'][1]
            return df_final['code'][0]
        else:
            return None

    def parse_diqu(self, quyu, page):
        """
        :param page: html 文本
        :return: diqu_code
        """
        if quyu.startswith('qg') or quyu.startswith('qycg') or quyu.endswith('quanguo') or quyu.startswith('zljianzhu') or quyu.startswith('daili'):
            txt_list = self.t_page(page)
            diqu_code = self.count_diqu(txt_list)
        else:

            diqu_code = self.xzqh_key_word_dict_list2[quyu]

        return diqu_code


page = '''
<table border="0" cellpadding="0" cellspacing="0" class="table2" width="640">
<tbody><tr align="center" bgcolor="#FAFAFA" valign="top">
<td height="201" style="BORDER-TOP: #cccccc 1px solid">
<div style="PADDING-TOP: 10px"></div>
<table border="0" cellpadding="0" cellspacing="0" width="580">
<tbody><tr valign="bottom">
<td height="40">
<div align="center"><font class="font20">汝阳县第二高级中学旧综合楼改造、室外零星及玻璃钢雨棚工程招标公告
</font></div>
</td>
</tr>
</tbody></table>
<table border="0" cellpadding="0" cellspacing="0" width="584">
<tbody>
<tr>
<td align="right" height="40" width="66%"><font color="#999999" face="Arial, Helvetica, sans-serif"><a href="http://www.ceiea.com" target="_blank"><font color="#999999">www.ceiea.com</font></a>
</font>    <font face="Arial, Helvetica, sans-serif">2019-08-12    中国教育装备网    
(7</font>)</td>
<td height="40" width="34%">
<table align="center" border="0" cellpadding="0" cellspacing="0" style="BORDER: #d5eaea 0px solid;">
<tbody>
<tr>
<td><font color="#999999">分享到： </font></td>
<td align="middle">
<div class="bdshare_t bds_tools get-codes-bdshare" data="{'pic':'http://127.0.0.1/3997131_094928081000_2.jpg'}" id="bdshare"><a class="bds_qzone" href="#" title="分享到QQ空间"></a>
<a class="bds_tsina" href="#" title="分享到新浪微博"></a> <a class="bds_tqq" href="#" title="分享到腾讯微博"></a> <span class="bds_more">更多</span>
<script data="type=tools&amp;uid=782182" id="bdshare_js" src="http://bdimg.share.baidu.com/static/js/bds_s_v2.js?cdnversion=434885" type="text/javascript"></script>
<script type="text/javascript"> 
    document.getElementById("bdshell_js").src = "http://bdimg.share.baidu.com/static/js/shell_v2.js?cdnversion=" + new Date().getHours();
</script>
</div>
</td>
</tr>
</tbody>
</table>
</td>
</tr>
</tbody>
</table>
<hr size="1" style="border:#E5E5E5 1px solid;" width="580"/>
<br/>
<table border="0" cellpadding="0" cellspacing="0" width="580">
<tbody>
<tr valign="bottom">
<td height="30" style="text-align:left;" valign="top"> <span class="font14"> </span>
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tbody>
<tr>
<td style="BORDER-RIGHT: #ffda8c 1px solid; PADDING-RIGHT: 5px; BORDER-TOP: #ffda8c 1px solid; PADDING-LEFT: 5px; PADDING-BOTTOM: 5px; BORDER-LEFT: #ffda8c 1px solid; LINE-HEIGHT: 16px; PADDING-TOP: 5px; BORDER-BOTTOM: #ffda8c 1px solid; BACKGROUND-COLOR: #ffffdd">
<table align="center" border="0" cellpadding="0" cellspacing="0" width="98%">
<tbody><tr>
<td rowspan="2" width="4%"><img height="14" src="/images/pao.gif" width="14"/>
<span style="line-height:200%"><br/>
</span></td>
<td width="96%">您未登陆，或您还不是<b>“教备网”</b>正式会员，当前不允许浏览招标信息！</td>
</tr>
<tr>
<td width="96%"><span style="line-height:200%">想获得浏览机会！请<a href="/l.htm" target="_blank"><font color="red"><u>登陆</u></font></a>
或 <a href="/r.htm" target="_blank"><font color="red"><u>注册</u></font></a>
成为“教备网”免费会员后<b><a href="/index.php?menu=upgrade" target="_blank"><font color="red">申请加入正式会员</font></a></b>。</span></td>
</tr>
<tr>
<td width="4%"> </td>
<td align="right" width="96%"><img height="8" src="dot.gif" width="8"/>
<a href="/index.php?menu=service" target="_blank"><u>查看会员服务内容</u></a></td>
</tr>
</tbody></table>
</td>
</tr>
</tbody>
</table>
<br/>
<span class="font14">
<div class="article">
</div><table align="center" bgcolor="#F6F6F6" border="0" cellpadding="7" cellspacing="6">
<tbody><tr bgcolor="#FFFFFF">
<td nowrap=""><img align="absmiddle" height="50" src="/images/ico-jg.gif" width="50"/>　<span class="font18">该正文内容您无权限浏览！</span></td>
</tr>
</tbody></table>
<p></p>
</span></td>
</tr>
</tbody>
</table>
<br/>
<p> </p>
<p><br/>
</p><hr size="1" style="border:#999999 1px dotted;" width="600"/>
<table align="center" border="0" cellpadding="0" cellspacing="0" width="580">
<tbody>
<tr align="left">
<td height="30"><b><font color="red">声明</font></b><font color="red">： 本网部分文章系中国教育装备网转载自其它媒体，目的在于信息传递，并不代表本网赞同其观点和对其真实性负责，如有新闻稿件和图片作品的内容、版权以及其它问题的，请联系我们。</font></td>
</tr>
</tbody>
</table>
<hr size="1" style="border:#999999 1px dotted;" width="600"/>
<br/>
<br/>
<table bgcolor="#E6E6E6" border="0" cellpadding="0" cellspacing="1" width="600">
<tbody><tr valign="bottom">
<td height="26" style="text-align:left;">
<table align="center" border="0" cellspacing="0" width="97%">
<tbody><tr>
<td bgcolor="#E6E6E6" class="font14" style="text-align:left;" width="50%"><b><font color="#CC0000">推荐企业</font></b></td>
<td align="right" width="50%"><a href="http://www.ceiea.com/zt/service/" target="_blank"><u>申请加入</u></a></td>
</tr>
</tbody></table>
</td>
</tr>
<tr>
<td bgcolor="#FFFFFF" height="130">
<div id="random_comp" style="text-align:left;"> <table align="center" border="0" width="97%">
<tbody>
<tr> <td><a href="http://www.ceiea.com/cp30047" target="_blank">飞生（上海）电子贸易有限公司</a></td> <td><a href="http://www.ceiea.com/cp48501" target="_blank"><b><font color="red">深圳市声菲特科技技术有限公司</font></b></a></td> <td><a href="http://www.ceiea.com/cp31317" target="_blank"><b><font color="red">广州市吉星信息科技有限公司</font></b></a></td> </tr> <tr> <td><a href="http://www.ceiea.com/cp53477" target="_blank"><b><font color="red">好易写（深圳）科技有限公司</font></b></a></td> <td><a href="http://www.ceiea.com/cp30128" target="_blank">深圳市艾博德科技股份有限公司</a></td> <td><a href="http://www.ceiea.com/cp54004" target="_blank">深圳伟东云教育科技有限公司</a></td> </tr> <tr> <td><a href="http://www.ceiea.com/cp41531" target="_blank">南京新立讯科技股份有限公司</a></td> <td><a href="http://www.ceiea.com/cp51555" target="_blank">广州市音桥电子科技有限公司</a></td> <td><a href="http://www.ceiea.com/cp52616" target="_blank">深圳市小柠檬教育科技有限公司</a></td> </tr> <tr> <td><a href="http://www.ceiea.com/cp12334" target="_blank">宁波华茂文教股份有限公司</a></td> <td><a href="http://www.ceiea.com/cp40806" target="_blank"><b><font color="red">青岛海信商用显示股份有限公司</font></b></a></td> <td><a href="http://www.ceiea.com/cp49628" target="_blank">北京易文汉学科技有限公司</a></td> </tr> <tr> <td><a href="http://www.ceiea.com/cp51457" target="_blank">深圳光峰科技股份有限公司</a></td> <td><a href="http://www.ceiea.com/cp47975" target="_blank">北京鑫三芙教学设备制造有限公司</a></td> <td><a href="http://www.ceiea.com/cp52432" target="_blank">北京微视酷科技有限责任公司</a></td> </tr>
</tbody>
</table>
</div>
<script language="javascript">
            $("random_comp").innerHTML ="正在加载...";
            $.post("/activepage/article_bottom.php?menu=getrandom",{},function(result){
                $("#random_comp").html(result);
            });
        </script>
</td>
</tr>
</tbody>
</table>
<br/>
<table bgcolor="#E6E6E6" border="0" cellpadding="0" cellspacing="1" width="600">
<tbody><tr valign="bottom">
<td height="26" style="text-align:left;">
<table align="center" border="0" cellspacing="0" width="97%">
<tbody><tr>
<td bgcolor="#E6E6E6" class="font14" style="text-align:left;" width="50%"><b>行业访谈</b></td>
<td align="right" width="50%"><a href="/indexhtml/interview_info.shtml"><u>更多专访</u></a></td>
</tr>
</tbody></table>
</td>
</tr>
</tbody><tbody>
<tr>
<td bgcolor="#FFFFFF" height="187">
<table border="0" cellpadding="0" cellspacing="5" width="100%">
<tbody>
<tr align="center" valign="top">
<td align="center"><a class="bt05_2012" href="http://www.ceiea.com/html/201904/201904270038293810.shtml" target="_blank" title="中广上洋田媛媛：智慧教育 融创未来"><img border="0" height="88" onerror="this.src='/images/nopic.gif';" src="/UserFiles/201905/1557205365.jpg" style="border:1 solid #c8c9c4" width="125"/><br/>
中广上洋田媛媛：智慧教育 融创未来</a> </td>
<td align="center"><a class="bt05_2012" href="http://www.ceiea.com/html/201904/201904272329592162.shtml" target="_blank" title="立达信王科研：全护眼照明解决方案 学校照明行业风向标"><img border="0" height="88" onerror="this.src='/images/nopic.gif';" src="/UserFiles/201905/1557205742.jpg" style="border:1 solid #c8c9c4" width="125"/><br/>
立达信王科研：全护眼照明解决方案 学校照明行业风向标</a> </td>
<td align="center"><a class="bt05_2012" href="http://www.ceiea.com/html/201904/201904272330035866.shtml" target="_blank" title="极光尔沃徐欢：坚持技术创新 赋能教育3D打印"><img border="0" height="88" onerror="this.src='/images/nopic.gif';" src="/UserFiles/201905/1557205653.jpg" style="border:1 solid #c8c9c4" width="125"/><br/>
极光尔沃徐欢：坚持技术创新 赋能教育3D打印</a> </td>
<td align="center"><a class="bt05_2012" href="http://www.ceiea.com/html/201904/201904272150598928.shtml" target="_blank" title="鸿合科技李水平：助力信息化教育改革 开启智慧教育新篇章"><img border="0" height="88" onerror="this.src='/images/nopic.gif';" src="/UserFiles/201905/1557205440.jpg" style="border:1 solid #c8c9c4" width="125"/><br/>
鸿合科技李水平：助力信息化教育改革 开启智慧教育新篇章</a> </td>
</tr> <tr align="center" valign="top">
<td align="center"><a class="bt05_2012" href="http://www.ceiea.com/html/201904/20190427232921317.shtml" target="_blank" title="佳比亚张永赋：新品亮相 满足多样市场需求"><img border="0" height="88" onerror="this.src='/images/nopic.gif';" src="/UserFiles/201905/1557205989.jpg" style="border:1 solid #c8c9c4" width="125"/><br/>
佳比亚张永赋：新品亮相 满足多样市场需求</a> </td>
<td align="center"><a class="bt05_2012" href="http://www.ceiea.com/html/201904/201904270038132913.shtml" target="_blank" title="中庆周少林：赋能智慧教育生态 构建教育资源建设"><img border="0" height="88" onerror="this.src='/images/nopic.gif';" src="/UserFiles/201905/1557205822.jpg" style="border:1 solid #c8c9c4" width="125"/><br/>
中庆周少林：赋能智慧教育生态 构建教育资源建设</a> </td>
<td align="center"><a class="bt05_2012" href="http://www.ceiea.com/html/201904/201904291557538630.shtml" target="_blank" title="奥威亚王书伟：创新共赢，协同赋能，全力部署智慧教育生态圈"><img border="0" height="88" onerror="this.src='/images/nopic.gif';" src="/UserFiles/201905/1557205617.jpg" style="border:1 solid #c8c9c4" width="125"/><br/>
奥威亚王书伟：创新共赢，协同赋能，全力部署智慧教育生态圈</a> </td>
<td align="center"><a class="bt05_2012" href="http://www.ceiea.com/html/201904/201904272329276644.shtml" target="_blank" title="长虹教育黄焕：独有云上校园 赋力智慧教育"><img border="0" height="88" onerror="this.src='/images/nopic.gif';" src="/UserFiles/201905/1557205069.jpg" style="border:1 solid #c8c9c4" width="125"/><br/>
长虹教育黄焕：独有云上校园 赋力智慧教育</a> </td>
</tr> <tr align="center" valign="top"> </tr>
</tbody>
</table>
</td>
</tr>
</tbody>
</table>
<p></p>
<div style="PADDING-TOP: 10px"><br/>
<p> </p>
<p><br/>
</p>
</div>
</td>
</tr>
</tbody></table>

'''


if __name__ == '__main__':
    """
    可直接跳过实例化。
    用法：p_diqu = parseDiqu(quyu, page)
    
    """
    # page = ''
    # contentlist = pd.read_excel(r'C:\Users\Administrator\Desktop\quyu_total_list.xlsx')
    # contentlist2 = contentlist['quyu'].values.tolist()
    # for cont in contentlist2 :

    p_diqu = parseDiqu('qycg_www_ceiea_com', page)
    print('quyu', p_diqu)
    # page1 = BeautifulSoup(page,'html.parser')
    # h1 = page1.find(string=re.compile('xx|相关'))
    # print(h1)
    pass