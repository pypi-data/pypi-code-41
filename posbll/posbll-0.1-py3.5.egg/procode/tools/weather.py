# coding=utf-8
from urllib import request
import re
import pinyin.pinyin as pinyin
import json
import time
from lxml import etree

#省份对应的省会城市
pc_city = {
  "anhui": "hefei",
  "beijing": "beijing",
  "chongqing": "chongqing",
  "fujian": "fuzhou",
  "gansu": "lanzhou",
  "guangdong": "GuangZhou",
  "guangxi": "NanNing",
  "guizhou": "GuiYang",
  "hainan": "HaiKou",
  "hebei": "ShiJiaZhuang",
  "heilongjiang": "HaErBin",
  "henan": "ZhengZhou",
  "xianggang": "xianggang",
  "hubei": "WuHan",
  "hunan": "ChangSha",
  "neimenggu": "HuHeHaoTe",
  "jiangsu": "NanJing",
  "jiangxi": "NanChang",
  "jilin": "ChangChun",
  "liaoning": "ShenYang",
  "aomen": "aomen",
  "ningxia": "YinChuan",
  "qinghai": "XiNing",
  "shanxi": "XiAn",
  "shandong": "JiNan",
  "shanghaishi": "shanghai",
  "shanx": "TaiYuan",
  "sichuan": "ChengDu",
  "tianjin": "tianjin",
  "xizang": "LaSa",
  "xinjiang": "WuLuMuQi",
  "yunnan": "KunMing",
  "zhejiang": "HangZhou",
  "taiwang": "TaiBei"
}


def getweather():
    res = request.urlopen('http://pv.sohu.com/cityjson')
    city_info = res.read().decode('gbk')
    print(city_info)
    addr = str(city_info).split('=')[1].split(',')[2].split('"')[3]  # 取出地址信息
    py = pinyin.get(addr, format='strip')
    provice = py.split('sheng', 1)[0].replace(' ', '')  # 获取省份


    city=None
    try:
        city = py.split('shi')[0].split('sheng')[
            1].strip().replace(' ', '')  # 获取城市
    except Exception as e:
        city=None

    #通过IP获取省份、城市时，要是城市没有获取到，那么就直接取该省份的省会城市
    if not city or city==None :
        for k, v in pc_city.items():
            if k == provice or k in provice:
                city = v
                break

    url = 'http://qq.ip138.com/weather/%s/%s.htm' % (provice, city)

    if city=="shanghai":
        url = 'http://qq.ip138.com/weather/%s' % (city)

    # 分析url可知某省某市的天气url即为上面格式
    wea_info = request.urlopen(url).read().decode('gbk')

    # 解析html，获取一周天气里当天天气
    tree = etree.HTML(wea_info)
    nodes = tree.xpath("/descendant::table[@class='t12']/tr")
    n_nodes = nodes[1:]

    weathers = []
    for n in range(len(n_nodes)):
        items = n_nodes[n].xpath("td")
        weathers_items = []
        for r in items:
            if r.text is None:
                tq = r.xpath("img")
                qt_str = ''
                for i_tq in tq:
                    if qt_str == '':
                        qt_str = i_tq.get("alt")
                    else:
                        qt_str = qt_str + "转" + i_tq.get("alt")
                weathers_items.append(qt_str)
            else:
                weathers_items.append(r.text)
        weathers.append(weathers_items)

    # 从一周天气信息中取出当天天气
    # print(time.localtime())
    n_time = time.localtime()
    n_year = n_time.tm_year
    n_mon = n_time.tm_mon
    n_day = n_time.tm_mday
    todayweather = {
        "date": "",
        "weather": "",
        "temperature": "",
        "wind": "",
        "addr": "",
        "icon": ""}
    for i in range(len(weathers[0])):
        if weathers[0][i].find(
                str(n_year) + "-" + str(n_mon) + "-" + str(n_day)) != -1:
            for j in range(len(weathers)):
                if j == 0:
                    todayweather["date"] = weathers[j][i]
                elif j == 1:
                    todayweather["weather"] = weathers[j][i]
                    if str(weathers[j][i]).find("转"):
                        n_weather = str(weathers[j][i]).split("转")[-1]
                    else:
                        n_weather = str(weathers[j][i])

                    if str(n_weather).find("雨") >= 0:
                        todayweather["icon"] = r"&#xe649;"
                    elif str(n_weather).find("雪") >= 0:
                        todayweather["icon"] = r"&#xe64b;"
                    elif str(n_weather).find("晴") >= 0:
                        todayweather["icon"] = r"&#xe64d;"
                    elif str(n_weather).find("阴") >= 0:
                        todayweather["icon"] = r"&#xe64c;"
                    elif str(n_weather).find("多云") >= 0:
                        todayweather["icon"] = r"&#xe64e;"
                    elif str(n_weather).find("雨夹雪") >= 0:
                        todayweather["icon"] = r"&#xe64a;"
                    else:
                        todayweather["icon"] = r"&#xe64d;"
                elif j == 2:
                    todayweather["temperature"] = weathers[j][i]
                elif j == 3:
                    todayweather["wind"] = weathers[j][i]
        else:
            continue
    todayweather["addr"] = addr

    return todayweather


