import datetime
import pandas as pd
from bs4 import BeautifulSoup
import re
import time


def ext_from_ggtime(ggstart_time):
    t1 = ggstart_time
    a = re.findall('([1-9][0-9]{3})[\-\./\\年]([0-9]{1,2})[\-\./\\月]([0-9]{1,2}) ([0-9]{2}):([0-9]{2}):([0-9]{2})', t1)

    if a != []:
        y = a[0]
        x = y[0] + "-" + (y[1] if len(y[1]) == 2 else '0%s' % y[1]) + '-' + (y[2] if len(y[2]) == 2 else '0%s' % y[2])
        return x

    a = re.findall('([1-9][0-9]{3})[\-\./\\年]([0-9]{1,2})[\-\./\\月]([0-9]{1,2})', t1)
    if a != []:
        y = a[0]
        x = y[0] + "-" + (y[1] if len(y[1]) == 2 else '0%s' % y[1]) + '-' + (y[2] if len(y[2]) == 2 else '0%s' % y[2])
        return x

    a = re.findall('^([0-2][0-9])[\-\./\\年]([0-9]{1,2})[\-\./\\月]([0-9]{1,2})', t1)
    if a != []:
        y = a[0]
        x = y[0] + "-" + (y[1] if len(y[1]) == 2 else '0%s' % y[1]) + '-' + (y[2] if len(y[2]) == 2 else '0%s' % y[2])
        x = '20' + x
        return x

    a = re.findall('^(20[0-9]{2})--([0-9]{1,2})-([0-9]{1,2})', t1)

    if a != []:
        x = '-'.join([a[0][0], a[0][1] if a[0][1] != '0' else '1', a[0][2] if a[0][2] != '0' else '1'])

        return x

    if ' CST ' in t1:
        try:
            x = time.strptime(t1, '%a %b %d %H:%M:%S CST %Y')
            x = time.strftime('%Y-%m-%d %H:%M:%S', x)
        except:
            x = ''
        if x != '': return x
    a = re.findall('^(20[0-9]{6})', t1)
    if a != []:
        x = '-'.join([a[0][:4], a[0][4:6], a[0][6:8]])
        return x

    return None


def extime_fbsj(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = "(?:发布时间|信息时间|录入时间|发稿时间)[：:](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})"
    a = re.findall(p, txt.replace('documentwrite', ''))
    if a != []:
        return '-'.join(a[0])
    return None


def extime(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/\.]', '', soup.text.strip())
    p = "(?:更新日期|变更日期|更新时间|发文日期|发表时间|公示日期|发布于|公告时间|公示时间|发布日期)[：:](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})"
    a = re.findall(p, txt.replace('documentwrite', ''))
    # print(a)
    if a != []:
        return '-'.join(a[0])
    return None


def extime_xxsj(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = "(?:信息时间)[：:](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})"
    a = re.findall(p, txt.replace('documentwrite', ''))
    # print(a)
    if a != []:
        return '-'.join(a[0])
    return None


def extime_guangdong_guangdongsheng_zfcg(ggstart_time, page):
    list1 = []
    soup = BeautifulSoup(page, 'lxml')
    soup_input = soup.find_all('input')[-3:]
    for i in soup_input:
        value = i['value']
        list1.append(value)
    if list1 != []:
        return ('-'.join([list1[0], list1[1], list1[2]]))
    return None


def extime_transfrom_yunan(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '(?:发布时间|提交时间|公示时间)[：:]{0,1}(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'

    a = re.findall(p, txt)
    if a != []:
        return ('-'.join(a[0]))
    return None


def strptime_transfrom_yue_r_n(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = re.sub('^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/', '', soup.text.strip())
    p = "(?:信息时间|信息日期|信息发布日期|发稿时间|发布时间|生成日期)[：:]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})[\-\.\\日/](20[0-2][0-9])"
    a = re.findall(p, txt)
    if a != []:
        return (a[0][2] + '-' + a[0][0] + '-' + a[0][1])
    return None


def extime_xxsj_v2(ggstart_time, page):
    res = extime_xxsj(ggstart_time, page)
    if not res:
        return res
    else:
        return ggstart_time


def extime_fbsj_v2(ggstart_time, page):
    # if ggstart_time is not None:
    #     res = ggstart_time
    # else:
    #     res = extime_fbsj(ggstart_time, page)
    res = extime_fbsj(ggstart_time, page)
    if not res:
        return res
    else:
        return ggstart_time


def extime_v2(ggstart_time, page):
    res = extime(ggstart_time, page)
    if not res:
        return res
    else:
        return ggstart_time


def extime_qg_1_zfcg(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.find_all('div', attrs={'class': 'pages_date'})
    if txt != []:
        txt = soup.find_all('div', attrs={'class': 'pages_date'})[0]
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
        return None
    return None


def extime_daili_www_xhtc_com_cn(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.find_all('div', attrs={'class': 'newstime'})
    if txt != []:
        txt_span = soup.find_all('div', attrs={'class': 'newstime'})[0]
        txt = txt_span.find('span')
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
        return None
    return None


def extime_henan_henansheng_1_daili(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.find_all('div', attrs={'class': 'infos'})
    if txt != []:
        txt = soup.find_all('div', attrs={'class': 'infos'})[0]
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
        return None
    return None


def extime_ningxia_ningxiasheng_zfcg_ningxia_yinchuan_zfcg(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.find_all('span', attrs={'id': 'pubTime'})
    if txt != []:
        txt = soup.find_all('span', attrs={'id': 'pubTime'})[0]
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
        return None
    return None


def extime_shandong_qingdao_zfcg(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.find_all('div', attrs={'class': 'biaotq'})
    if txt != []:
        txt = soup.find_all('div', attrs={'class': 'biaotq'})[0]
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
        return None
    return


def extime_qycg_eps_hnagroup_com(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = "(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})发布"
    a = re.findall(p, txt.replace('documentwrite', ''))
    # print(a)
    if a != []:
        return '-'.join(a[0])
    return None


def extime_daili_www_cfet_com_cn(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.find_all('span', attrs={'id': 'pubTime'})
    if txt != []:
        txt = soup.find_all('span', attrs={'id': 'pubTime'})[0]
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
        return None
    return None


def extime_sichuan_luzhou_ggzy(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.find_all('p', attrs={'class': 'news-article-info'})
    if txt != []:
        txt_pan = soup.find_all('p', attrs={'class': 'news-article-info'})[0]
        # print(txt_pan)
        # txt=txt_pan.find('span',attrs={'class':'infos'})
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt_pan.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
    else:
        txt = soup.find_all('div', attrs={'class': 'ewb-results-date'})
        if txt != []:
            txt = soup.find_all('div', attrs={'class': 'ewb-results-date'})[0]
            txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
            p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
            a = re.findall(p, txt.replace('documentwrite', ''))
            if a != []:
                return '-'.join(a[0])
            return None


def extime_liaoning_huludao_ggzy(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.find_all('td', attrs={'class': 'title_main2'})
    if txt != []:
        txt = soup.find_all('td', attrs={'class': 'title_main2'})[0]
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
        return None
    else:
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
        p = '信息日期[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
        return None


def extime_jiangxi_dexing_ggzy1(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.find_all('div', attrs={'class': 'property'})
    txt1 = soup.find_all('p', attrs={'class': 'infotime'})
    if txt != []:
        txt_span = soup.find_all('div', attrs={'class': 'property'})[0]
        txt = txt_span.find('span')
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
    elif txt1 != []:
        txt = soup.find_all('p', attrs={'class': 'infotime'})[0]
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
    else:
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
        p = '发布日期[:：]{0,1}(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
    return None


def extime_guangxi_baise_gcjs(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.find_all('div', attrs={'class': 'info'})
    if txt != []:
        txt_span = soup.find_all('div', attrs={'class': 'info'})[0]
        txt = txt_span.find_all('span')[0]
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
        return None
    return None


def extime_tail(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    tmp = soup.find('style')
    if tmp is not None:
        tmp.clear()
    tmp = soup.find('script')
    if tmp is not None:
        tmp.clear()
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a = re.findall(p, txt[-40:])
    if a != []:
        return '-'.join(a[0])
    return None


def extime_shanxi_hanzhong_gcjs(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    tmp = soup.find('style')
    if tmp is not None:
        tmp.clear()
    tmp = soup.find('script')
    if tmp is not None:
        tmp.clear()
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '(?:公示日期|公示时间)[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a = re.findall(p, txt)
    if a != []:
        return '-'.join(a[0])
    else:
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt[-40:])
        if a != []:
            return '-'.join(a[-1])
    return None


def extime_shandong_shandongsheng_gcjs(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    tmp = soup.find('style')
    if tmp is not None:
        tmp.clear()
    tmp = soup.find('script')
    if tmp is not None:
        tmp.clear()
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '(发布日期[:：]20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a = re.findall(p, txt)
    if a != []:
        return '-'.join(a[0])
    else:
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt[-40:])
        if a != []:
            return '-'.join(a[-1])
    return None


def extime_shandong_zoucheng_ggzy(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    tmp = soup.find('style')
    if tmp is not None:
        tmp.clear()
    tmp = soup.find('script')
    if tmp is not None:
        tmp.clear()
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '(?:发布时间|公示时间|公示期自)[:：]{0,1}[自]{0,1}(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a = re.findall(p, txt)
    if a != []:
        return '-'.join(a[0])
    else:
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt[-40:])
        if a != []:
            return '-'.join(a[0])
    return None


def extime_daili_www_kanti_cn(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    tmp = soup.find('style')
    if tmp is not None:
        tmp.clear()
    tmp = soup.find('script')
    if tmp is not None:
        tmp.clear()
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '(?:发布时间|公示时间)[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a = re.findall(p, txt)
    if a != []:
        return '-'.join(a[0])
    else:
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt[-40:])
        if a != []:
            return '-'.join(a[0])
    return None


def extime_qycg_www_zmzb_com(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.find_all('span', attrs={'id': 'zdsj'})
    if txt != []:
        txt = soup.find_all('span', attrs={'id': 'zdsj'})[0]
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
        return None
    else:
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt[-40:])
        if a != []:
            return '-'.join(a[0])
    return None


def extime_jiangxi_yingtan_ggzy(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    tmp = soup.find('style')
    if tmp is not None:
        tmp.clear()
    tmp = soup.find('script')
    if tmp is not None:
        tmp.clear()
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/\[\]]', '', soup.text.strip())
    # txt=soup.text
    pattren = ['\[(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})\]',
               '生成日期[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',
               '发布日期[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',
               ]
    for p in pattren:

        a = re.findall(p, txt)
        if a != []:
            return '-'.join(a[0])
    return None


def extime_shandong_dongying_gcjs(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    tmp = soup.find('style')
    if tmp is not None:
        tmp.clear()
    tmp = soup.find('script')
    if tmp is not None:
        tmp.clear()
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '(?:发布日期|公示时间|报名时间)[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a = re.findall(p, txt)
    if a != []:
        return '-'.join(a[0])
    else:
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt[-40:])
        if a != []:
            return '-'.join(a[0])
        return None


def extime_sichuan_suining_ggzy(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.find_all('p', attrs={'class': 'time1'})
    if txt != []:
        txt = soup.find_all('p', attrs={'class': 'time1'})[0]
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
    else:
        txt = soup.find_all('p', attrs={'class': 'time'})
        if txt != []:
            txt = soup.find_all('p', attrs={'class': 'time'})[0]
            txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
            p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
            a = re.findall(p, txt.replace('documentwrite', ''))
            if a != []:
                return '-'.join(a[0])
    return None


def extime_xizang_xizangsheng_ggzy(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    tmp = soup.find('style')
    if tmp is not None:
        tmp.clear()
    tmp = soup.find('script')
    if tmp is not None:
        tmp.clear()
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '(?:发布时间|公示时间)[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a = re.findall(p, txt)
    if a != []:
        return '-'.join(a[0])
    else:
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt[-40:])
        if a != []:
            return '-'.join(a[0])
        return None


def extime_qycg_b2b_10086_cn(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    tmp = soup.find('style')
    if tmp is not None:
        tmp.clear()
    tmp = soup.find('script')
    if tmp is not None:
        tmp.clear()
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a = re.findall(p, txt[-100:])
    if a != []:
        return '-'.join(a[-1])
    return None


def extime_beijing_beijingshi_gcjs(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    tmp = soup.find('style')
    if tmp is not None:
        tmp.clear()
    tmp = soup.find('script')
    if tmp is not None:
        tmp.clear()
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '(?:招标登记日期|发布日期|公示日期[:：])(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a = re.findall(p, txt)
    if a != []:
        return '-'.join(a[0])
    else:
        p = '日期[:：]{0,1}(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt[-200:])
        if a != []:
            return '-'.join(a[-1])
        return None


def extime_gansu_wuwei_ggzy(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    tmp = soup.find('style')
    if tmp is not None:
        tmp.clear()
    tmp = soup.find('script')
    if tmp is not None:
        tmp.clear()
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '(?:竞价(公告)开始时间)(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a = re.findall(p, txt)
    if a != []:
        return '-'.join(a[0])
    else:
        return ggstart_time


def extime_guangxi_qinzhou_zfcg(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.find_all('ul', attrs={'class': 'xvd'})
    if txt != []:
        txt = soup.find_all('ul', attrs={'class': 'xvd'})[0]
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
    return None


def extime_heilongjiang_daqing_ggzy(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    tmp = soup.find('style')
    if tmp is not None:
        tmp.clear()
    tmp = soup.find('script')
    if tmp is not None:
        tmp.clear()
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '(?:发布时间|开标日期)[:：]{0,1}(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a = re.findall(p, txt)
    if a != []:
        return '-'.join(a[0])
    else:
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt[-40:])
        if a != []:
            return '-'.join(a[0])
        return ggstart_time


def extime_henan_henansheng_gcjs(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '日期[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a = re.findall(p, txt)
    if a != []:
        return '-'.join(a[0])
    return None


def extime_hubei_macheng_ggzy(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.find_all('li', attrs={'class': 'list-group-item'})
    if txt != []:
        txt = soup.find_all('li', attrs={'class': 'list-group-item'})[0]
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
    else:
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
        p = '(?:公示时间|公告发布时间)[:：]{0,1}(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt)
        if a != []:
            return '-'.join(a[0])
    return ggstart_time


def extime_jiangsu_jiangsusheng_gcjs(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    tmp = soup.find('style')
    if tmp is not None:
        tmp.clear()
    tmp = soup.find('script')
    if tmp is not None:
        tmp.clear()
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/\[\]]', '', soup.text.strip())
    pattren = [
        '公示期自[:：]{0,1}(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.月\\/]([0-9]{,2})',
        '公示开始时间[:：]{0,1}(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.月\\/]([0-9]{,2})',
        '公示起[始止]时间[:：]{0,1}(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.月\\/]([0-9]{,2})',
        '发布日期为(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.月\\/]([0-9]{,2})']
    for p in pattren:
        a = re.findall(p, txt)
        if a != []:

            return '-'.join(a[0])
    return ggstart_time


def extime_liaoning_haicheng_ggzy(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '公告期限[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a = re.findall(p, txt)
    if a != []:
        return '-'.join(a[0])
    else:
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt[-100:])
        if a != []:
            return '-'.join(a[-1])
    return ggstart_time


def extime_liaoning_liaoningsheng_ggzy(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    tmp = soup.find('style')
    if tmp is not None:
        tmp.clear()
    tmp = soup.find('script')
    if tmp is not None:
        tmp.clear()
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a = re.findall(p, txt[-100:])
    if a != []:
        return '-'.join(a[0])
    return ggstart_time


def extime_qycg_fwgs_sinograin_com_cn(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    try:
        txt = soup.find_all('h2')
        txt[0].find('div').clear()
    except:
        txt = []

    if txt != []:
        txt = soup.find_all('h2')[0]

        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
    return None


def extime_guangxi_guangxisheng_gcjs(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    tmp = soup.find('style')
    if tmp is not None:
        tmp.clear()
    tmp = soup.find('script')
    if tmp is not None:
        tmp.clear()
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '(?:公告日期|公示开始时间)[:：]{0,1}(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a1 = re.findall(p, txt)
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a2 = re.findall(p, txt[-40:])
    if a1 != []:
        return '-'.join(a1[0])
    elif a2 != []:
        return '-'.join(a2[0])
    else:
        txt = soup.text
        txt = txt.replace('\n', '')
        p = '(?:报名开始时间)[:：]{0,1}(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt)
        if a != []:
            return '-'.join(a[0])
    return ggstart_time


def extime_liaoning_tieling_ggzy(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    # print(1111,txt)
    p = "(?:公告发布时间|发布时间[:：])(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})"
    a = re.findall(p, txt.replace('documentwrite', ''))
    # print(a)
    if a != []:
        return '-'.join(a[0])


def extime_liaoning_liaoningsheng_zfcg(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    p = '(?:公告期限|录入时间|领取谈判文件时间、地点|报名时间)[:：]{0,1}(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/\、]', '', soup.text.strip())
    a = re.findall(p, txt)
    if a != []:
        return '-'.join(a[0])
    return ggstart_time
