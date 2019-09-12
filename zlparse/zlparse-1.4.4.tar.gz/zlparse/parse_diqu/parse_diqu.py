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
        print(json_path)
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
        jieba.del_word('上海银行')
        jieba.add_word('蛇口')
        jieba.del_word('浙江医药')
        jieba.add_word('江西师范大学')
        jieba.suggest_freq(("中山", "大学"), False)
        self.data['code'] = self.data['code'].astype('str')
        # shape[0] 首个
        # print(self.data.shape  )shape  数据框格式
        for i in list(range(self.data.shape[0])):
            # 去掉省的后四位，市的后两位。
            if len(self.data['code'][i]) > 2 and len(self.data['code'][i]) <7:
                grup = []
                num = 0
                temp=''
                for j in self.data['code'][i]:
                    grup.append(j)
                grup.reverse()
                temp = ''.join(grup)
                for k in temp:
                    if k == '0':
                        num = num + 1
                    else:
                        break
                if num > 1:
                    # print(num)
                    self.data['code'][i] = self.data['code'][i][:-num]
                if len(self.data['code'][i])%2!=0:
                    self.data['code'][i]=self.data['code'][i]+"0"
                # if len(self.data['code'][i][2:])==2:
                #     if self.data['code'][i][2:]=='00':
                #         self.data['code'][i]=self.data['code'][i][:2]
                # else:
                #    if self.data['code'][i][2:]=='0000':
                #        self.data['code'][i] = self.data['code'][i][:2]
                #    else:
                #        if self.data['code'][i][4:] == '00':
                #            self.data['code'][i] = self.data['code'][i][:4]
            else:
                # if len(self.data['code'][i])>6:
                #     if self.data['code'][i][-5:]=='00000':
                #         self.data['code'][i]=self.data['code'][i][:-5]
                #     else:
                #         if self.data['code'][i][-4:]=='0000':
                #             self.data['code'][i] = self.data['code'][i][:-4]
                #         else:
                #             if self.data['code'][i][-3:]=='000':
                #                 self.data['code'][i] = self.data['code'][i][:-3]
                #     self.data['code'][i]=self.data['code'][i][:6]
                grup = []
                num = 0
                temp=''
                for j in self.data['code'][i]:
                    grup.append(j)
                grup.reverse()
                temp = ''.join(grup)
                for k in temp:
                    if k == '0':
                        num = num + 1
                    else:
                        break
                if num > 0 and len(self.data['code'][i])>6:
                    # print(num)
                    self.data['code'][i] = self.data['code'][i][:-num]

                if len(self.data['code'][i])%2!=0:
                    self.data['code'][i]=self.data['code'][i]+"0"

                # if re.findall('[0-9][0-9][0]{4}', self.data['code'][i]):
                #     self.data['code'][i] = self.data['code'][i][:2]
                # else:
                #     self.data['code'][i] = self.data['code'][i][:4]

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

    def key_word_or_all_page(self,object_list,txt_list):
        print('key_word_or_all_page','ok')
        if re.findall("(?:招标人|采购人|采购人名称|采购人地址|交货地点|项目所在地区|项目名称|项目地点|招标代理机构)[:：](.{0,20})", txt_list):
            txt2 = re.findall("(?:招标人|采购人|采购人名称|采购人地址|交货地点|项目所在地区|项目名称|项目地点|招标代理机构)[:：](.{0,20})", txt_list)[0]
            for word in jieba.cut(txt2, cut_all=True):
                print(word)
                if word in self.new_diqu_list:
                    object_list.append(self.data['code'][self.data['word'] == word].tolist()[0])
            if object_list == []:
                for word in jieba.cut(txt_list, cut_all=True):
                    if word in self.new_diqu_list:
                        object_list.append(self.data['code'][self.data['word'] == word].tolist()[0])
        else:
            for word in jieba.cut(txt_list, cut_all=True):
                if word in self.new_diqu_list:
                    object_list.append(self.data['code'][self.data['word'] == word].tolist()[0])

    def count_diqu(self, txt_list):
        object_list = []
        if self.soup.find('h1') :
            txt1 = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', self.soup.find('h1').text.strip())
            if '中山大学' in txt_list:
                for word in jieba.cut(txt_list, cut_all=False):
                    if word in self.new_diqu_list:
                        object_list.append(self.data['code'][self.data['word'] == word].tolist()[0])
            else:
                for word in jieba.cut(txt_list, cut_all=True):
                    if word in self.new_diqu_list:
                        object_list.append(self.data['code'][self.data['word'] == word].tolist()[0])
            if object_list == []:
                self.key_word_or_all_page(object_list, txt_list)

        elif self.soup.find(string=re.compile('工程|项目|公告|大学')):
            txt1 = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', self.soup.find(string=re.compile('工程|项目|公告|大学')).strip())
            if '中山大学' in txt_list:
                for word in jieba.cut(txt_list, cut_all=False):
                    if word in self.new_diqu_list:
                        object_list.append(self.data['code'][self.data['word'] == word].tolist()[0])
            else:
                for word in jieba.cut(txt_list, cut_all=True):
                    if word in self.new_diqu_list:
                        object_list.append(self.data['code'][self.data['word'] == word].tolist()[0])
            if object_list == []:
                self.key_word_or_all_page(object_list, txt_list)
        else:
            self.key_word_or_all_page(object_list, txt_list)
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
            print(df_final)
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





if __name__ == '__main__':
    """
    可直接跳过实例化。
    用法：p_diqu = parseDiqu(quyu, page)
    
    """
    page = ''
    # contentlist = pd.read_excel(r'C:\Users\Administrator\Desktop\quyu_total_list.xlsx')
    # contentlist2 = contentlist['quyu'].values.tolist()
    # for cont in contentlist2 :
    txt='''

<!doctype html>
<html>
<head>
<meta charset="UTF-8" />
<title>中盐新干盐化有限公司Q2卤井修复改造工程项目[0703-1940CIC2P109]-招标公告_南网招标_</title>
<meta name="keywords" content="中盐新干盐化有限公司Q2卤井修复改造工程项目[0703-1940CIC2P109]-招标公告南网招标,资讯国家电网_电网建设_中国南方电力_国家能源局_供电局_省电网_中国南方电网" />
<meta name="description" content="中盐新干盐化有限公司Q2卤井修复改造工程项目[0703-1940CIC2P109]-招标公告" />
<meta http-equiv="mobile-agent" content="format=html5;url=http://m.dlztb.com/news/201909/09/346.html">
<link rel="shortcut icon" type="image/x-icon" href="http://www.dlztb.com/favicon.ico" />
<link rel="bookmark" type="image/x-icon" href="http://www.dlztb.com/favicon.ico" />
<link rel="stylesheet" type="text/css" href="http://www.dlztb.com/skin/default/style.css" />
<link rel="stylesheet" type="text/css" href="http://www.dlztb.com/skin/default/article.css" />
<!--[if lte IE 6]>
<link rel="stylesheet" type="text/css" href="http://www.dlztb.com/skin/default/ie6.css"/>
<![endif]-->
<script type="text/javascript">window.onerror=function(){return true;}</script><script type="text/javascript" src="http://www.dlztb.com/lang/zh-cn/lang.js"></script>
<script type="text/javascript" src="http://www.dlztb.com/file/script/config.js"></script>
<!--[if lte IE 9]><!-->
<script type="text/javascript" src="http://www.dlztb.com/file/script/jquery-1.5.2.min.js"></script>
<!--<![endif]-->
<!--[if (gte IE 10)|!(IE)]><!-->
<script type="text/javascript" src="http://www.dlztb.com/file/script/jquery-2.1.1.min.js"></script>
<!--<![endif]-->
<script type="text/javascript" src="http://www.dlztb.com/file/script/common.js"></script>
<script type="text/javascript" src="http://www.dlztb.com/file/script/page.js"></script>
<script type="text/javascript" src="http://www.dlztb.com/file/script/jquery.lazyload.js"></script><script type="text/javascript">
var searchid = 21;
</script>
</head>
<body>
<div class="head" id="head">
<div class="head_m">
<div class="head_r" id="destoon_member"></div>
<div class="head_l">
<ul>
<li class="h_fav"><script type="text/javascript">addFav('收藏本页');</script></li>
<li class="h_mobile"><a href="javascript:Dmobile();">手机版</a></li><li class="h_qrcode"><a href="javascript:Dqrcode();">二维码</a></li><li class="h_cart"><a href="http://www.dlztb.com/member/cart.php">购物车</a>(<span class="head_t" id="destoon_cart">0</span>)</li></ul>
</div>
</div>
</div>
<div class="m head_s" id="destoon_space"></div>
<div class="m"><div id="search_tips" style="display:none;"></div></div>
<div id="destoon_qrcode" style="display:none;"></div><div class="m">
<div id="search_module" style="display:none;" onmouseout="Dh('search_module');" onmouseover="Ds('search_module');">
<ul>
<li onclick="setModule('21','资讯')">资讯</li><li onclick="setModule('23','招标')">招标</li><li onclick="setModule('24','项目')">项目</li><li onclick="setModule('25','中标')">中标</li><li onclick="setModule('7','行情')">行情</li><li onclick="setModule('26','华能')">华能</li><li onclick="setModule('27','大唐')">大唐</li><li onclick="setModule('28','华电')">华电</li><li onclick="setModule('29','国电')">国电</li><li onclick="setModule('30','国家电投')">国家电投</li><li onclick="setModule('31','国家能源')">国家能源</li><li onclick="setModule('22','招商')">招商</li><li onclick="setModule('6','询价')">询价</li><li onclick="setModule('42','招标代理')">招标代理</li></ul>
</div>
</div>
<div class="m">
<div class="logo f_l"><a href="http://www.dlztb.com/"><img src="http://www.dlztb.com/file/upload/201804/17/112553861.jpg" alt="中国电力招标采购网" /></a></div>
<form id="destoon_search" action="http://www.dlztb.com/news/search.php" onsubmit="return Dsearch(1);">
<input type="hidden" name="moduleid" value="21" id="destoon_moduleid" />
<input type="hidden" name="spread" value="0" id="destoon_spread" />
<div class="head_search">
<div>
<input name="kw" id="destoon_kw" type="text" class="search_i" value="请输入关键词" onfocus="if(this.value=='请输入关键词') this.value='';" onkeyup="STip(this.value);" autocomplete="off" x-webkit-speech speech /><input type="text" id="destoon_select" class="search_m" value="资讯" readonly onfocus="this.blur();" onclick="$('#search_module').fadeIn('fast');" /><input type="submit" value=" " class="search_s" />
</div>
</div>
</form>
<div class="head_search_kw f_l"><a href="" onclick="Dsearch_top();return false;"><strong>推广</strong></a>
<a href="" onclick="Dsearch_adv();return false;"><strong>热搜：</strong></a>
<span id="destoon_word"><a href="http://www.dlztb.com/news/search.php?kw=%E5%85%AC%E5%91%8A">公告</a>&nbsp; <a href="http://www.dlztb.com/news/search.php?kw=%E5%85%AC%E5%8F%B8">公司</a>&nbsp; <a href="http://www.dlztb.com/news/search.php?kw=%E6%9C%8D%E5%8A%A1">服务</a>&nbsp; <a href="http://www.dlztb.com/news/search.php?kw=%E5%B7%A5%E7%A8%8B%E6%8B%9B%E6%A0%87%E5%85%AC%E5%91%8A">工程招标公告</a>&nbsp; <a href="http://www.dlztb.com/news/search.php?kw=%E6%9C%BA%E7%BB%84">机组</a>&nbsp; <a href="http://www.dlztb.com/news/search.php?kw=%E7%A5%9E%E5%8D%8E">神华</a>&nbsp; <a href="http://www.dlztb.com/news/search.php?kw=%E9%9B%86%E4%B8%AD">集中</a>&nbsp; <a href="http://www.dlztb.com/news/search.php?kw=%E5%8C%96%E5%B7%A5">化工</a>&nbsp; <a href="http://www.dlztb.com/news/search.php?kw=%E9%85%8D%E7%94%B5">配电</a>&nbsp; <a href="http://www.dlztb.com/news/search.php?kw=%E4%BA%BA%E6%B0%91%E5%8C%BB%E9%99%A2">人民医院</a>&nbsp; </span></div>
</div>
<div class="m">
<div class="menu">
<ul><li><a href="http://www.dlztb.com/"><span>首页</span></a></li><li><a href="http://m.dlztb.com/app.apk" target="_blank"><span style="color:#800000;">app下载</span></a></li><li class="menuon"><a href="http://www.dlztb.com/news/"><span style="color:#993300;">资讯</span></a></li><li><a href="http://www.dlztb.com/zbxx/" target="_blank"><span style="color:#800000;">招标</span></a></li><li><a href="http://www.dlztb.com/xmxx/" target="_blank"><span style="color:#800000;">项目</span></a></li><li><a href="http://www.dlztb.com/zbgg/" target="_blank"><span style="color:#800000;">中标</span></a></li><li><a href="http://www.dlztb.com/quote/"><span style="color:#800000;">行情</span></a></li><li><a href="http://www.dlztb.com/hpi/" target="_blank"><span style="color:#800000;">华能</span></a></li><li><a href="http://www.dlztb.com/chinapowerbid/" target="_blank"><span style="color:#800000;">大唐</span></a></li><li><a href="http://www.dlztb.com/chdtp/" target="_blank"><span style="color:#800000;">华电</span></a></li><li><a href="http://www.dlztb.com/powerec/" target="_blank"><span style="color:#800000;">国电</span></a></li><li><a href="http://www.dlztb.com/cpeinet/" target="_blank"><span style="color:#800000;">国家电投</span></a></li><li><a href="http://www.dlztb.com/shzb/" target="_blank"><span style="color:#800000;">国家能源</span></a></li><li><a href="http://www.dlztb.com/invest/" target="_blank"><span>招商</span></a></li><li><a href="http://www.dlztb.com/zbxx/search.php?kw=%E6%A0%B8%E7%94%B5&fields=0&catid=0&order=0" target="_blank"><span style="color:#FF0000;">核电</span></a></li><li><a href="http://www.dlztb.com/buy/" target="_blank"><span style="color:#000080;">询价</span></a></li><li><a href="http://txl.dlztb.com/" target="_blank"><span style="color:#800080;">业主</span></a></li><li><a href="http://www.dlztb.com/member/alert.php?action=add&mid=23" target="_blank"><span style="color:#FF0000;">招标定制</span></a></li><li><a href="http://www.dlztb.com/zbdl/" target="_blank"><span>招标代理</span></a></li></ul>
</div>
</div>
<div class="m b20" id="headb"></div>
<script>
(function(){
    var bp = document.createElement('script');
    var curProtocol = window.location.protocol.split(':')[0];
    if (curProtocol === 'https') {
        bp.src = 'https://zz.bdstatic.com/linksubmit/push.js';
    }
    else {
        bp.src = 'http://push.zhanzhang.baidu.com/push.js';
    }
    var s = document.getElementsByTagName("script")[0];
    s.parentNode.insertBefore(bp, s);
})();
</script><script type="text/javascript">var module_id= 21,item_id=346,content_id='content',img_max_width=800;</script>
<div class="m">
<div class="nav"><div>分享<img src="http://www.dlztb.com/skin/default/image/ico-share.png" class="share" title="分享好友" onclick="Dshare(21, 346);" /></div><a href="http://www.dlztb.com/">首页</a> <i>&gt;</i> <a href="http://www.dlztb.com/news/">资讯</a> <i>&gt;</i> <a href="http://www.dlztb.com/news/138.html">南网招标</a></div>
<div class="b20 bd-t"></div>
</div>
<div class="m m3">
<div class="m3l">
<h1 class="title" id="title">中盐新干盐化有限公司Q2卤井修复改造工程项目[0703-1940CIC2P109]-招标公告</h1>
<div class="info"><span class="f_r"><img src="http://www.dlztb.com/skin/default/image/ico-zoomin.png" width="16" height="16" title="放大字体" class="c_p" onclick="fontZoom('+', 'article');" />&nbsp;&nbsp;<img src="http://www.dlztb.com/skin/default/image/ico-zoomout.png" width="16" height="16" title="缩小字体" class="c_p" onclick="fontZoom('-', 'article');" /></span>
日期：2019-09-09&nbsp;&nbsp;&nbsp;&nbsp;
来源：<a href="http://www.dlztb.com" target="_blank">中国电力招标采购网</a>&nbsp;&nbsp;&nbsp;&nbsp;作者：dlztb&nbsp;&nbsp;&nbsp;&nbsp;浏览：<span id="hits">1</span>&nbsp;&nbsp;&nbsp;&nbsp;</div>
<div id="content"><div class="content" id="article"><div class="Co<em></em>ntnet Jknr" style="min-height:500px; padding:0 30px;">
招标公告
<P LANG="ar-SA" CLASS="cjk" ALIGN=CENTER data="margin-bottom: 0cm"><SPAN LANG="en-US">(</SPAN>招标编号：<SPAN LANG="en-US">0703-1940CIC2P109<SPAN data="background: transparent">)</SPAN></SPAN></P>
<P LANG="ar-SA" CLASS="cjk" data="margin-top: 0.21cm; margin-bottom: 0cm; line-height: 150%">
项目所在地区：<SPAN LANG="zh-CN">江西</SPAN>省</P>
<P LANG="ar-SA" CLASS="cjk" data="margin-top: 0.21cm; margin-bottom: 0cm; line-height: 150%">
一、招标条件</P>
<P LANG="ar-SA" data="text-indent: 0.74cm; margin-top: 0.11cm; margin-bottom: 0.11cm; line-height: 0.71cm">
<SPAN data="text-decoration: none">本</SPAN>中盐新干盐化 <SPAN LANG="en-US">Q2</SPAN>卤井修复改造工程项目已具备招标条件，<SPAN LANG="zh-CN">中仪国际招标 </SPAN> 受<SPAN LANG="zh-CN">中盐新干盐化 </SPAN> 的委托，现对该项目进行公开招标。</P>
<P LANG="ar-SA" CLASS="cjk" data="margin-top: 0.21cm; margin-bottom: 0cm; line-height: 150%">
二、招标概况与招标范围</P>
<P LANG="ar-SA" CLASS="cjk" ALIGN=LEFT data="text-indent: 0.74cm; margin-bottom: 0cm; line-height: 0.64cm">
工程名称：中盐新干盐化 <SPAN LANG="en-US">Q2</SPAN>卤井修复改造工程项目</P>
<P LANG="ar-SA" CLASS="cjk" data="text-indent: 0.74cm; margin-bottom: 0cm; line-height: 0.92cm">
工程 </P>
<P LANG="ar-SA" CLASS="cjk" data="text-indent: 0.74cm; margin-bottom: 0cm; line-height: 0.92cm">
招标范围：施工现场范围内的所有工程内容<SPAN LANG="zh-CN">，以现场工程量为结算依据</SPAN>。</P>
<P LANG="ar-SA" CLASS="cjk" ALIGN=LEFT data="margin-bottom: 0cm; line-height: 0.64cm">
三、招标文件的获取</P>
<OL>
<OL>
<OL>
<OL>
<OL>
<OL TYPE=i>
<OL>
<OL>
<LI><P LANG="ar-SA" ALIGN=LEFT data="margin-top: 0.11cm; margin-bottom: 0.11cm; line-height: 150%">
<SPAN data="background: transparent">本项目招标文件采用网上审批下载方式发放，不向投标人提供纸质招标文件。招标文件发售日</SPAN>期为<SPAN LANG="en-US">201<SPAN LANG="en-US">9</SPAN></SPAN>年<SPAN LANG="en-US"><SPAN LANG="en-US">9</SPAN></SPAN>月<SPAN LANG="en-US"><SPAN LANG="en-US">9</SPAN></SPAN>日至<SPAN LANG="en-US">201<SPAN LANG="en-US">9</SPAN></SPAN>年<SPAN LANG="en-US"><SPAN LANG="en-US">9</SPAN></SPAN>月<SPAN LANG="en-US"><SPAN LANG="en-US">14</SPAN></SPAN>日。</P>
<LI><P LANG="ar-SA" ALIGN=LEFT data="margin-top: 0.11cm; margin-bottom: 0.11cm; line-height: 150%">
有意向的投标人应先在通用招标网<SPAN LANG="en-US"> .cn</SPAN>免费注册，注册完成后凭登陆账号浏览招标公告及预览招标文件 。如需购买，按照网上操作流程进行购买。技术支持电 </P>
未曾在<a href="http://www.dlztb.com/member/dlztb_register.php">中国电力招标采购网（www.dlztb.com）</a>上<a href="http://www.dlztb.com/member/dlztb_register.php">注册</a>会员的单位应先注册。登录成功后根据招标公告的相说明下载投标文件！<br />
<br />
<span style="font-family: 仿宋, 仿宋_GB2312; font-size: 18.6667px;">项目</span> <a href="http://www.dlztb.com/a&lt;em&gt;&lt;/em&gt;bout/copyright.html" target="_blank" style="word-break: break-all; font-family: " microsoft=""><span style="font-family: 仿宋, 仿宋_GB2312; font-size: 18.6667px;">联系人</span></a><span style="font-family: 仿宋, 仿宋_GB2312; font-size: 18.6667px;">：李杨</span> <span style="text-indent: 2em;">&nbsp;</span><span style="font-family: 仿宋, 仿宋_GB2312; font-size: 18.6667px;"><br />
</span> <span style="font-family: 仿宋, 仿宋_GB2312; font-size: 18.6667px;">咨询电话：010-51957458</span><span style="text-indent: 2em;">&nbsp;</span><span style="font-family: 仿宋, 仿宋_GB2312; font-size: 18.6667px;"><br />
</span> <span style="font-family: 仿宋, 仿宋_GB2312; font-size: 18.6667px;">传真：010-51957412</span><span style="text-indent: 2em;">&nbsp;</span><span style="font-family: 仿宋, 仿宋_GB2312; font-size: 18.6667px;"><br />
</span> <span style="font-family: 仿宋, 仿宋_GB2312; font-size: 18.6667px;">手机：13683233285</span><span style="text-indent: 2em;">&nbsp;</span><span style="font-family: 仿宋, 仿宋_GB2312; font-size: 18.6667px;"><br />
</span> <span style="font-family: 仿宋, 仿宋_GB2312; font-size: 18.6667px;">QQ:1211306049</span><span style="text-indent: 2em;">&nbsp;</span><span style="font-family: 仿宋, 仿宋_GB2312; font-size: 18.6667px;"><br />
</span> <span style="font-family: 仿宋, 仿宋_GB2312; font-size: 18.6667px;">微信：Li13683233285 邮箱：</span><span style="font-family: 仿宋, 仿宋_GB2312; font-size: 18.6667px;">1211306049@qq.com<br />
<br />
</P>
</P>
</P>
</P>
</P>
</P>
</P>
来源：<a href="http://www.dlztb.com/" target="_blank">中国电力招标采购网</a> 编辑：dlztb008
</p>
</p>
</p>
</p>
</p>china-ten</div>
</div>
<div class="b20 c_b">&nbsp;</div>
<div class="keytags">
<strong>标签：</strong>
<a href="http://www.dlztb.com/news/search.php?kw=%E4%B8%AD%E7%9B%90%E6%96%B0%E5%B9%B2%E7%9B%90%E5%8C%96%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8Q2%E5%8D%A4%E4%BA%95%E4%BF%AE%E5%A4%8D%E6%94%B9%E9%80%A0%E5%B7%A5%E7%A8%8B%E9%A1%B9%E7%9B%AE%5B0703-1940CIC2P109%5D-%E6%8B%9B%E6%A0%87%E5%85%AC%E5%91%8A" target="_blank" class="b">中盐新干盐化有限公司Q2卤井修复改造工程项目[0703-1940CIC2P109]-招标公告</a>
</div>
<div class="np">
<ul>
<li><strong>下一篇：</strong><a href="http://www.dlztb.com/news/201909/09/347.html" title="梅州市碧道建设总体规划公开招标公告">梅州市碧道建设总体规划公开招标公告</a>
</li>
<li><strong>上一篇：</strong><a href="http://www.dlztb.com/news/201909/09/345.html" title="龙华民治街道小微企业安全生产标准化建设指导服务">龙华民治街道小微企业安全生产标准化建设指导服务</a>
</li>
</ul>
</div>
<div class="b10">&nbsp;</div>
扫一扫快速入网
<table width="580" border="0">
<tr>
<td><div align="center"><a href="http://www.dlztb.com/about/copyright.html"><img src="http://www.dlztb.com/wx6800.png" width="128" height="128" border="0" /></a></div></td>
<td><div align="center"><a href="http://www.dlztb.com/about/copyright.html"><img src="http://www.dlztb.com/wx9800.png" width="128" height="128" border="0" /></a></div></td>
<td><div align="center"><a href="http://www.dlztb.com/about/copyright.html"><img src="http://www.dlztb.com/zfb6800.png" width="128" height="128" border="0" /></a></div></td>
<td><div align="center"><a href="http://www.dlztb.com/about/copyright.html"><img src="http://www.dlztb.com/zfb9800.png" width="128" height="128" border="0" /></a></div></td>
</tr>
</table>
<div class="award"><div onclick="Go('http://www.dlztb.com/member/award.php?mid=21&itemid=346');">打赏</div></div><div class="b20">&nbsp;</div>
<div class="head-txt"><span><a href="http://www.dlztb.com/news/search.php?kw=%E4%B8%AD%E7%9B%90%E6%96%B0%E5%B9%B2%E7%9B%90%E5%8C%96%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8Q2%E5%8D%A4%E4%BA%95%E4%BF%AE%E5%A4%8D%E6%94%B9%E9%80%A0%E5%B7%A5%E7%A8%8B%E9%A1%B9%E7%9B%AE%5B0703-1940CIC2P109%5D-%E6%8B%9B%E6%A0%87%E5%85%AC%E5%91%8A">更多<i>&gt;</i></a></span><strong>同类资讯</strong></div>
<div class="related"><table width="100%">
</table>
</div>
<br />
</div>
<div class="m3r">
<div class="head-sub"><strong>最新资讯</strong></div>
<div class="list-rank"><ul>
<li><span class="f_r">&nbsp;09-11</span><a href="http://www.dlztb.com/news/201909/11/2237.html" target="_blank" title="环岛路（大干围～南洲路）沥滘地铁站段道路升级改造工程施工总承包">环岛路（大干围～南洲路）沥滘地铁站段道路升级改造工程施工总承包</a></li>
<li><span class="f_r">&nbsp;09-11</span><a href="http://www.dlztb.com/news/201909/11/2236.html" target="_blank" title="环岛路（大干围～南洲路）沥滘地铁站段道路升级改造工程施工总承包">环岛路（大干围～南洲路）沥滘地铁站段道路升级改造工程施工总承包</a></li>
<li><span class="f_r">&nbsp;09-11</span><a href="http://www.dlztb.com/news/201909/11/2235.html" target="_blank" title="客村立交大修工程施工总承包">客村立交大修工程施工总承包</a></li>
<li><span class="f_r">&nbsp;09-11</span><a href="http://www.dlztb.com/news/201909/11/2234.html" target="_blank" title="客村立交大修工程施工总承包">客村立交大修工程施工总承包</a></li>
<li><span class="f_r">&nbsp;09-11</span><a href="http://www.dlztb.com/news/201909/11/2233.html" target="_blank" title="赤坎区公共文化服务中心">赤坎区公共文化服务中心</a></li>
<li><span class="f_r">&nbsp;09-11</span><a href="http://www.dlztb.com/news/201909/11/2232.html" target="_blank" title="赤坎区公共文化服务中心">赤坎区公共文化服务中心</a></li>
<li><span class="f_r">&nbsp;09-11</span><a href="http://www.dlztb.com/news/201909/11/2231.html" target="_blank" title="珠江琶醍啤酒文化创意园区改造升级项目-汽机锅炉间建筑改造施工项目（第二次）（补充公告）">珠江琶醍啤酒文化创意园区改造升级项目-汽机锅炉间建筑改造施工项目（第二次）（补充公告）</a></li>
<li><span class="f_r">&nbsp;09-11</span><a href="http://www.dlztb.com/news/201909/11/2230.html" target="_blank" title="珠江琶醍啤酒文化创意园区改造升级项目-汽机锅炉间建筑改造施工项目（第二次）（补充公告）">珠江琶醍啤酒文化创意园区改造升级项目-汽机锅炉间建筑改造施工项目（第二次）（补充公告）</a></li>
<li><span class="f_r">&nbsp;09-11</span><a href="http://www.dlztb.com/news/201909/11/2229.html" target="_blank" title="白云高新区●产业创新园第三方检测服务">白云高新区●产业创新园第三方检测服务</a></li>
<li><span class="f_r">&nbsp;09-11</span><a href="http://www.dlztb.com/news/201909/11/2228.html" target="_blank" title="白云高新区●产业创新园第三方检测服务">白云高新区●产业创新园第三方检测服务</a></li>
<li><span class="f_r">&nbsp;09-11</span><a href="http://www.dlztb.com/news/201909/11/2227.html" target="_blank" title="白云高新区●产业创新园监测服务">白云高新区●产业创新园监测服务</a></li>
<li><span class="f_r">&nbsp;09-11</span><a href="http://www.dlztb.com/news/201909/11/2226.html" target="_blank" title="白云高新区●产业创新园监测服务">白云高新区●产业创新园监测服务</a></li>
<li><span class="f_r">&nbsp;09-11</span><a href="http://www.dlztb.com/news/201909/11/2225.html" target="_blank" title="天地庙村人居环境标杆村打造项目">天地庙村人居环境标杆村打造项目</a></li>
<li><span class="f_r">&nbsp;09-10</span><a href="http://www.dlztb.com/news/201909/10/2224.html" target="_blank" title="华能大庆热电有限公司1号机组低压缸零出力供热改造EPC工程项目【重新招标】招标公告">华能大庆热电有限公司1号机组低压缸零出力供热改造EPC工程项目【重新招标】招标公告</a></li>
<li><span class="f_r">&nbsp;09-10</span><a href="http://www.dlztb.com/news/201909/10/2223.html" target="_blank" title="舞阳县商务局舞阳县电子商务进农村综合示范项目公开招标公告招标公告">舞阳县商务局舞阳县电子商务进农村综合示范项目公开招标公告招标公告</a></li>
<li><span class="f_r">&nbsp;09-10</span><a href="http://www.dlztb.com/news/201909/10/2222.html" target="_blank" title="揭阳供电局调度大楼、输变电大楼办公楼等日常维修（消防）及调度大楼档案室消防系统更换采购">揭阳供电局调度大楼、输变电大楼办公楼等日常维修（消防）及调度大楼档案室消防系统更换采购</a></li>
<li><span class="f_r">&nbsp;09-10</span><a href="http://www.dlztb.com/news/201909/10/2221.html" target="_blank" title="郑州铁路职业技术学院中国教育和科研计算机网带宽接入服务项目单一来源采购公告">郑州铁路职业技术学院中国教育和科研计算机网带宽接入服务项目单一来源采购公告</a></li>
<li><span class="f_r">&nbsp;09-10</span><a href="http://www.dlztb.com/news/201909/10/2220.html" target="_blank" title="揭阳供电局调度大楼、输变电大楼办公楼等日常维修（消防）及调度大楼档案室消防系统更换采购">揭阳供电局调度大楼、输变电大楼办公楼等日常维修（消防）及调度大楼档案室消防系统更换采购</a></li>
</ul>
</div>
<div class="head-sub"><strong>最新行情</strong></div>
<div class="list-rank"><ul>
<li><span class="f_r">&nbsp;09-10</span><a href="http://www.dlztb.com/quote/201909/24828.html" target="_blank" title="1号机组低压缸零出力供热改造EPC工程项目【重新招标】招标">1号机组低压缸零出力供热改造EPC工程项目【重新招标】招标</a></li>
<li><span class="f_r">&nbsp;09-10</span><a href="http://www.dlztb.com/quote/201909/24827.html" target="_blank" title="青海发投碱业有限公司食品添加剂碳酸钠1000kg（内袋）集装袋供应商采购项目招标公告">青海发投碱业有限公司食品添加剂碳酸钠1000kg（内袋）集装袋供应商采购项目招标公告</a></li>
<li><span class="f_r">&nbsp;09-10</span><a href="http://www.dlztb.com/quote/201909/24826.html" target="_blank" title="乌兰纳木格农牧有限公司乡村旅游建设项目询比采购公告">乌兰纳木格农牧有限公司乡村旅游建设项目询比采购公告</a></li>
<li><span class="f_r">&nbsp;09-10</span><a href="http://www.dlztb.com/quote/201909/24825.html" target="_blank" title="同仁县热贡六月会民俗同仁县热贡六月会民俗体验旅游基础设施建设项目（尕队村、东干木村）招标公告(资格后审)">同仁县热贡六月会民俗同仁县热贡六月会民俗体验旅游基础设施建设项目（尕队村、东干木村）招标公告(资格后审)</a></li>
<li><span class="f_r">&nbsp;09-10</span><a href="http://www.dlztb.com/quote/201909/24824.html" target="_blank" title="黄河李家峡水电站水轮机转轮改造工程---3#水轮机转轮改造工程施工监理招标公告">黄河李家峡水电站水轮机转轮改造工程---3#水轮机转轮改造工程施工监理招标公告</a></li>
<li><span class="f_r">&nbsp;09-10</span><a href="http://www.dlztb.com/quote/201909/24823.html" target="_blank" title="龙羊峡水电站330kV GIS室桥机及其附属设备采购招标公告">龙羊峡水电站330kV GIS室桥机及其附属设备采购招标公告</a></li>
<li><span class="f_r">&nbsp;09-10</span><a href="http://www.dlztb.com/quote/201909/24822.html" target="_blank" title="李家峡水电站水轮机转轮改造工程-制动器采购及伴随服务招标公告">李家峡水电站水轮机转轮改造工程-制动器采购及伴随服务招标公告</a></li>
<li><span class="f_r">&nbsp;09-10</span><a href="http://www.dlztb.com/quote/201909/24821.html" target="_blank" title="李家峡水电站水轮机转轮改造工程-发电机上盖板采购招标公告">李家峡水电站水轮机转轮改造工程-发电机上盖板采购招标公告</a></li>
<li><span class="f_r">&nbsp;09-10</span><a href="http://www.dlztb.com/quote/201909/24820.html" target="_blank" title="乌兰纳木格农牧有限公司乡村旅游建设项目公开询比采购公告">乌兰纳木格农牧有限公司乡村旅游建设项目公开询比采购公告</a></li>
<li><span class="f_r">&nbsp;09-10</span><a href="http://www.dlztb.com/quote/201909/24819.html" target="_blank" title="国家电投西宁、西安新能源生产运营中心PaaS云平台及光伏电站智能运维诊断系统建设（一期）招标公告">国家电投西宁、西安新能源生产运营中心PaaS云平台及光伏电站智能运维诊断系统建设（一期）招标公告</a></li>
<li><span class="f_r">&nbsp;09-10</span><a href="http://www.dlztb.com/quote/201909/24818.html" target="_blank" title="多巴新城风情东路公交场站建设项目招标公告">多巴新城风情东路公交场站建设项目招标公告</a></li>
<li><span class="f_r">&nbsp;09-10</span><a href="http://www.dlztb.com/quote/201909/24817.html" target="_blank" title="多巴新城风情东路公共停车场建设项目招标公告">多巴新城风情东路公共停车场建设项目招标公告</a></li>
<li><span class="f_r">&nbsp;09-10</span><a href="http://www.dlztb.com/quote/201909/24816.html" target="_blank" title="青海省海南州千万千瓦级新能源基地（一区两园）3000兆瓦光伏项目电力工程基础设施35kV预制舱式汇集站采购招标公告">青海省海南州千万千瓦级新能源基地（一区两园）3000兆瓦光伏项目电力工程基础设施35kV预制舱式汇集站采购招标公告</a></li>
<li><span class="f_r">&nbsp;09-10</span><a href="http://www.dlztb.com/quote/201909/24815.html" target="_blank" title="青海省海南州千万千瓦级新能源基地（一区两园）3000兆瓦光伏项目电力工程基础设施1#330kV汇集站40.5kV高原型开关柜设备及共箱母线采购招标公告">青海省海南州千万千瓦级新能源基地（一区两园）3000兆瓦光伏项目电力工程基础设施1#330kV汇集站40.5kV高原型开关柜设备及共箱母线采购招标公告</a></li>
<li><span class="f_r">&nbsp;09-10</span><a href="http://www.dlztb.com/quote/201909/24814.html" target="_blank" title="格尔木机务段含油废水排水管网及污水处理设备改造工程施工监理(第二次)投标邀请公告">格尔木机务段含油废水排水管网及污水处理设备改造工程施工监理(第二次)投标邀请公告</a></li>
<li><span class="f_r">&nbsp;09-10</span><a href="http://www.dlztb.com/quote/201909/24813.html" target="_blank" title="青海省海南州千万千瓦级新能源基地（一区两园）3000兆瓦光伏项目电力工程基础设施1#、2#、3# 330kV汇集站土建及机电安装工程招标公告">青海省海南州千万千瓦级新能源基地（一区两园）3000兆瓦光伏项目电力工程基础设施1#、2#、3# 330kV汇集站土建及机电安装工程招标公告</a></li>
<li><span class="f_r">&nbsp;09-10</span><a href="http://www.dlztb.com/quote/201909/24812.html" target="_blank" title="雨汪煤矿一井轻轨采购项目招标">雨汪煤矿一井轻轨采购项目招标</a></li>
<li><span class="f_r">&nbsp;09-10</span><a href="http://www.dlztb.com/quote/201909/24811.html" target="_blank" title="青海省海南州千万千瓦级新能源基地（一区两园）3000兆瓦光伏项目电力工程基础设施35kV汇集站土建及机电安装工程及35kV集电线路工程（A包、B包）招标公告">青海省海南州千万千瓦级新能源基地（一区两园）3000兆瓦光伏项目电力工程基础设施35kV汇集站土建及机电安装工程及35kV集电线路工程（A包、B包）招标公告</a></li>
</ul>
</div>
</div>
<div class="c_b"></div>
</div>
<script type="text/javascript" src="http://www.dlztb.com/file/script/content.js"></script><div class="m b20" id="footb"></div>
<div class="m">
<div class="foot_page">
<a href="http://www.dlztb.com/">网站首页</a> &nbsp;|&nbsp;
<a href="http://www.dlztb.com/about/11.html">授权书</a> &nbsp;|&nbsp;
<a href="http://www.dlztb.com/about/10.html">认证审核</a> &nbsp;|&nbsp;
<a href="http://www.dlztb.com/about/8.html">银行汇款</a> &nbsp;|&nbsp;
<a href="http://www.dlztb.com/about/7.html">信用评价</a> &nbsp;|&nbsp;
<a href="http://www.dlztb.com/about/5.html">服务说明</a> &nbsp;|&nbsp;
<a href="http://www.dlztb.com/about/index.html">关于我们</a> &nbsp;|&nbsp;
<a href="http://www.dlztb.com/about/contact.html">联系方式</a> &nbsp;|&nbsp;
<a href="http://www.dlztb.com/about/agreement.html">使用协议</a> &nbsp;|&nbsp;
<a href="http://www.dlztb.com/about/copyright.html">银行汇款</a> &nbsp;|&nbsp;
<a href="http://www.dlztb.com/sitemap/">网站地图</a> &nbsp;|&nbsp;
<a href="http://www.dlztb.com/spread/">排名推广</a> &nbsp;|&nbsp;
<a href="http://www.dlztb.com/ad/">广告服务</a> &nbsp;|&nbsp; <a href="http://www.dlztb.com/gift/">积分换礼</a> &nbsp;|&nbsp; <a href="http://www.dlztb.com/feed/">RSS订阅</a> &nbsp;|&nbsp; <a href="javascript:SendReport();">违规举报</a>
&nbsp;|&nbsp; <a href="http://www.miibeian.gov.cn" target="_blank">京ICP备12017752号-8</a></div>
</div>
<div class="m">
<div class="foot">
<div id="copyright">总机：010-51957458客服部010-51957412 招标部01052883525微信号13683233285   24小时移动13683233285联通13126614855 <br />经营许可证号：京ICP证070736号工商局网站注册编号:010202008032700008<br />许可证号：京ICP备12017752号-8<br />电力招标官方网备案资质查询：<a href="http://www.hd315.gov.cn/beian/view.asp?bianhao=010202008032700008">http://www.hd315.gov.cn/beian/view.asp?bianhao=010202008032700008</a></strong></p>中文域名如下，可的地址栏中直接输入访问<br /><a href="http://www.dlztb.com/about/index.html">http://www.dlztb.com/about/index.html</a></div>
</div>
</div>
<script>(function(){
var src = (document.location.protocol == "http:") ? "http://js.passport.qihucdn.com/11.0.1.js?23b7972fc88013f86fd470dc4d93b1e5":"https://jspassport.ssl.qhimg.com/11.0.1.js?23b7972fc88013f86fd470dc4d93b1e5";
document.write('<script src="' + src + '" id="sozz"><\/script>');
})();
</script>
<div class="back2top"><a href="javascript:void(0);" title="返回顶部">&nbsp;</a></div>
<script type="text/javascript">
show_task('moduleid=21&html=show&itemid=346&page=1');
$(function(){$("img").lazyload();});</script>
<script type="text/javascript" src="https://s5.cnzz.com/z_stat.php?id=1276897203&web_id=1276897203"></script>
</body>
</html>
'''


    p_diqu = parseDiqu('qycg_www_ceiea_com', '四川凉山彝族自治州盐源县卫生健康局2019预防接种门诊医用冰箱采购项目招标公告')
    print('quyu', p_diqu)
    # page1 = BeautifulSoup(page,'html.parser')
    # h1 = page1.find(string=re.compile('xx|相关'))
    # print(h1)
    pass