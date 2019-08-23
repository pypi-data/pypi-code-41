import random
from collections import OrderedDict
from datetime import datetime
from math import ceil
from urllib import parse
import pandas as pd
import requests
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
from zlsrc.util.etl import est_html, add_info, est_meta_large, est_meta
from zlsrc.util.fake_useragent import UserAgent



tt_url = None
payloadData = None

end_time = datetime.strftime(datetime.now(), "%Y-%m-%d")

datetime_now = datetime.now()
datetime_three_month_ago = datetime_now - relativedelta(months=3)
start_time = datetime_three_month_ago.strftime('%Y-%m-%d')
def f1_requests(driver, num):
        try:
            proxies_data = webdriver.DesiredCapabilities.CHROME
            proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
            proxy = proxies_chromeOptions[0].split('=')[1]
            proxies = {'http': '%s' % proxy}
        except:
            proxies = {}
        user_agents = UserAgent()
        user_agent = user_agents.chrome
        headers = {
            'User-Agent': user_agent,
        }
        Dats = {
            'pageIndex': num,
            'pageSize': 15,
            'pointPageIndexId': num-1,
            'operateDateFrom': '{}'.format(start_time),
            'operateDateTo': '{}'.format(end_time),
        }
        datas = {**payloadData, **Dats}
        # print(datas)
        # 下载超时
        timeOut = 120
        time.sleep(random.uniform(1, 3))
        if proxies:
            res = requests.post(url=tt_url, headers=headers, data=datas, proxies=proxies, timeout=timeOut)
        else:
            res = requests.post(url=tt_url, headers=headers, data=datas, timeout=timeOut)
        # 需要判断是否为登录后的页面
        if res.status_code != 200:
            raise ConnectionError
        else:
            html = res.text
            soup = BeautifulSoup(html, 'html.parser')
            uls = soup.find("ul", class_="m_m_c_list")
            if '没有数据' in uls.text.strip():
                return pd.DataFrame()
            lis = uls.find_all("li")
            data = []
            for tr in lis:
                a = tr.find_all('a')
                try:
                    title = a[-1]['title'].strip()
                except:
                    title = a[-1].text.strip()
                td = tr.find('em').text.strip()
                href = a[-1]['href'].strip()
                if 'http' in href:
                    link = href
                else:
                    link = 'http://www.gdgpo.gov.cn' + href
                span = tr.find('span').text.strip()
                info = {}
                try:
                    leixing = span.split('·')[0].split('[')[1].strip()
                    diqu = span.split('·')[1].split(']')[0].strip()
                    info['lx'] = leixing
                    info['diqu'] = diqu
                except:
                    diqu = span.split('[')[1].split(']')[0].strip()
                    info['diqu'] = diqu
                if info:
                    info = json.dumps(info, ensure_ascii=False)
                else:
                    info = None
                tmp = [title, td, link, info]
                data.append(tmp)
            df = pd.DataFrame(data=data)
            return df


def f1(driver, num):
    n = 0
    while n < 6:
        try:
            time.sleep(2 * n)
            df = f1_requests(driver, num)
            return df
        except:
            n += 1


def f2(driver):
    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s' % proxy}
    except:
        proxies = {}
    global tt_url,payloadData
    tt_url=''
    start_url = driver.current_url
    payloadData = {}
    for st in start_url.rsplit('&'):
        if 'http' in st:
            tt_url = st
            continue
        sz = st.split('=')
        payloadData[sz[0]] = parse.unquote(sz[1], 'utf-8')
    n = 0
    page_num = None
    while n < 6:
        try:
            time.sleep(2 * n)
            page_num = get_pageall(tt_url, payloadData,proxies)
            break
        except:
            n += 1

    driver.quit()
    return int(page_num)





def get_pageall(tt_url, payloadData,proxies):
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'User-Agent': user_agent,
    }
    Data = {
        'pageIndex': 1,
        'pageSize': 15,
        'pointPageIndexId': 1,
        'operateDateFrom': '{}'.format(start_time),
        'operateDateTo': '{}'.format(end_time),
    }
    datas = {**Data, **payloadData}
    # print(datas)
    # 下载超时
    timeOut = 120
    time.sleep(random.uniform(1, 3))
    res = requests.post(url=tt_url, headers=headers, data=datas,proxies=proxies, timeout=timeOut)
    # 需要判断是否为登录后的页面
    if res.status_code != 200:
        raise ConnectionError
    else:
        html = res.text
        soup = BeautifulSoup(html, 'html.parser')
        uls = soup.find("ul", class_="m_m_c_list")
        if '没有数据' in uls.text.strip():
            return 0
        try:
            total = soup.find_all('span', class_='aspan')[-1].text.strip()
            num = int(total)
        except:
            total = soup.find('form', attrs={'name':"qPageForm"}).font.text.strip()
            num = ceil(int(total)/15)
        return num


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='zw_c_c_cont'][string-length()>150]")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    before = len(driver.page_source)
    time.sleep(1)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(0.1)
        after = len(driver.page_source)
        i += 1
        if i > 5: break
    page = driver.page_source
    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', class_='zw_c_cont')
    return div




def get_data():
    data = []
    sitewebName = OrderedDict([
        ("汕头市", "汕头市,南澳县,澄海区,潮阳区,潮南区,濠江区,龙湖区,金平区")
    ])

    sitewebId = OrderedDict([
        ("汕头市",
         "4028889705bebb510105becdbed40009,297e6a6a49176e84014917f3953f0e3b,297e6a6a49176e84014917f25f800e3a,297e6a6a49176e84014917f177060e39,297e6a6a49176e84014917f08b320e38,297e6a6a49176e84014917eeaf460c0d,297e6a6a49176e84014917edca26052e,297e6a6a49176e84014917ea40500024"),
    ])

    regionIds = OrderedDict([("汕头市", "0104")])

    channelCode = OrderedDict([("zhaobiao", "0005"), ("biangeng", "0006"), ("zhongbiao", "0008"),("gqita_fanpai", "0017"), ("gqita_zhao_liu_pljz", "-3")])

    # 省级采购
    for w1 in channelCode.keys():
        for w2 in sitewebName.keys():
            p1 = sitewebId[w2]
            p2 = regionIds[w2]
            href = "http://www.gdgpo.gov.cn/queryMoreInfoList.do&channelCode=%s&sitewebName=%s&sitewebId=%s&regionIds=%s" \
                   % (channelCode[w1], sitewebName[w2],p1, p2)
            tb = "zfcg_%s_sj_diqu%s_gg" % (w1, p2)
            col = ["name", "ggstart_time", "href", "info"]
            tmp = [tb, href, col, add_info(f1, {"diqu1": w2}), f2]
            data.append(tmp)

    sx_sitewebId = OrderedDict([
        ("汕头市", "4028889705bebb510105becdbed40009"),
                                 ])

    # 市县采购
    for w1 in channelCode.keys():
        for w2 in sx_sitewebId.keys():
            p2 = regionIds[w2]
            href = "http://www.gdgpo.gov.cn/queryMoreCityCountyInfoList2.do&channelCode=%s&sitewebId=%s" % (channelCode[w1], sx_sitewebId[w2])
            tb = "zfcg_%s_sx_diqu%s_gg" % (w1, p2)
            col = ["name", "ggstart_time", "href", "info"]
            tmp = [tb, href, col, add_info(f1, {"diqu1": w2}), f2]
            data.append(tmp)
    data1 = data.copy()
    remove_arr = []
    for w in data:
        if w[0] in remove_arr: data1.remove(w)
    return data1
    # 创建data

data = get_data()

# print(data)

def work(conp, **args):
    est_meta(conp, data=data, diqu="广东省汕头市", **args)
    est_html(conp, f=f3, **args)


# 修改日期：2019/7/11
# 页数太多，跑不完，总是会跳回首页，详情页加载慢
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "shantou1"],pageloadtimeout=120,interval_page=10)

    # driver=webdriver.Chrome()
    # url = "http://www.gdgpo.gov.cn/queryMoreInfoList.do&channelCode=0006&sitewebName=梅州市,蕉岭县,平远县,五华县,丰顺县,大埔县,兴宁市,梅县区,梅江区&sitewebId=4028889705bedd7e0105beec36890004,297e6a6a49176e840149182a8a500e7d,297e6a6a49176e8401491829dfb00e7c,297e6a6a49176e840149182916880e7b,297e6a6a49176e8401491828272c0e7a,297e6a6a49176e8401491827381d0e79,297e6a6a49176e84014918267e7f0e78,297e6a6a49176e8401491825c7fd0e77,297e6a6a49176e8401491824f18d0e76&regionIds=0108"
    # driver.get(url)
    # df = f2(driver)
    # print(df)
    # driver=webdriver.Chrome()
    # url = "http://www.gdgpo.gov.cn/queryMoreInfoList.do&channelCode=0006&sitewebName=梅州市,蕉岭县,平远县,五华县,丰顺县,大埔县,兴宁市,梅县区,梅江区&sitewebId=4028889705bedd7e0105beec36890004,297e6a6a49176e840149182a8a500e7d,297e6a6a49176e8401491829dfb00e7c,297e6a6a49176e840149182916880e7b,297e6a6a49176e8401491828272c0e7a,297e6a6a49176e8401491827381d0e79,297e6a6a49176e84014918267e7f0e78,297e6a6a49176e8401491825c7fd0e77,297e6a6a49176e8401491824f18d0e76&regionIds=0108"
    # driver.get(url)
    # for i in range(1, 10):
    #     df=f1(driver, i)
    #     print(df.values)
