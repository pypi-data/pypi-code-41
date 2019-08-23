import random
from collections import OrderedDict
from datetime import datetime
from math import ceil
from urllib import parse
import pandas as pd
import re
import requests
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
from zlsrc.util.etl import est_html, add_info, est_meta_large
from zlsrc.util.fake_useragent import UserAgent



end_time = datetime.strftime(datetime.now(), "%Y-%m-%d")

datetime_now = datetime.now()
datetime_three_month_ago = datetime_now - relativedelta(months=3)
start_time = datetime_three_month_ago.strftime('%Y-%m-%d')

def f1_data(driver, num):
    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s' % proxy}
    except:
        proxies = ''
    user_agents = UserAgent()
    user_agent = user_agents.chrome
    headers = {
        'User-Agent': user_agent,
    }
    if 'queryPlanList.do' in tt_url:
        Dats = {
            'pageIndex': num,
            'pageSize': 15,
            'pointPageIndexId': num - 1,
            'manOrgAnswerDateFrom': '{}'.format(start_time),
            'manOrgAnswerDateTo': '{}'.format(end_time),
            "levelStatus": "",
            "planContent.auditNumber": "",
            "planContent.demandDate3": "",
            "planContent.govBuyServiceContent": "",
            "planContent.govBuyServiceType": "",
            "planContent.pppPlankType": "",
            "planContent.projectName": "",
            "planContent.stockIndexName": "",
            "planContent.unitOrg.name": "",
            "regionCode": "",
        }

    elif 'queryCityPlanList.do' in tt_url:
        Dats = {
            'pageIndex': num,
            'pageSize': 15,
            'pointPageIndexId': num - 1,
            'manOrgAnswerDateFrom': '{}'.format(start_time),
            'manOrgAnswerDateTo': '{}'.format(end_time),
            "planContent.auditNumber": "",
            "planContent.demandDate3": "",
            "planContent.govBuyServiceContent": "",
            "planContent.govBuyServiceType": "",
            "planContent.pppPlankType": "",
            "planContent.projectName": "",
            "planContent.stockIndexName": "",
            "planContent.stockType.id": "",
            "planContent.unitOrg.name": "",
            "siteCode": "",
        }

    datas = {**payloadData, **Dats}
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
        uls = soup.find("div", class_="m_m_cont").table
        if '没有数据' in uls.text.strip():
            return pd.DataFrame()
        lis = uls.find_all("tr")
        data = []
        for tr in lis[1:]:
            a = tr.find_all('a', class_='c_m_check')[-1]
            name = tr.find_all('td')[3]['title']
            ggstart_time = tr.find_all('td')[-4].text.strip()
            href = a['href'].strip()
            if 'http' in href:
                link = href
            else:
                link = 'http://www.gdgpo.gov.cn' + href
            info = {}

            if tr.find_all('td')[1]:
                cgr = tr.find_all('td')[1]['title']
                if cgr: info['cgr'] = cgr
            if tr.find_all('td')[2]:
                xm_num = tr.find_all('td')[2].text.strip()
                if xm_num: info['xm_num'] = xm_num
            if tr.find_all('td')[4]:
                cgp = tr.find_all('td')[4].text.strip()
                if cgp: info['cgp'] = cgp
            if tr.find_all('td')[5]:
                money = tr.find_all('td')[5].text.strip()
                if money: info['money'] = money
            if tr.find_all('td')[6]:
                number = tr.find_all('td')[6].text.strip()
                if number: info['number'] = number
            if tr.find_all('td')[7]:
                cgfs = tr.find_all('td')[7].text.strip()
                if cgfs: info['cgfs'] = cgfs

            if info:
                info = json.dumps(info, ensure_ascii=False)
            else:
                info = None
            tmp = [name, ggstart_time, link, info]
            data.append(tmp)
        df = pd.DataFrame(data=data)
        return df


def f1_requests(driver, num):
        try:
            proxies_data = webdriver.DesiredCapabilities.CHROME
            proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
            proxy = proxies_chromeOptions[0].split('=')[1]
            proxies = {'http': '%s' % proxy}
        except:
            proxies = ''
        user_agents = UserAgent()
        user_agent = user_agents.chrome
        headers = {
            'User-Agent': user_agent,
        }
        if 'queryAcceptanceList.do' in tt_url:
            Dats = {
                'pageIndex': num,
                'pageSize': 15,
                'pointPageIndexId': num-1,
                'submitTimeFrom': '{}'.format(start_time),
                'submitTimeTo': '{}'.format(end_time),
                "acceptance.contractTitle.contractName": "",
                "acceptance.operator": "",
                "acceptance.result": "",
                "acceptance.contractTitle.planSno": "",
            }

        elif 'queryCityAcceptanceList.do' in tt_url:
            Dats = {
                'pageIndex': num,
                'pageSize': 15,
                'pointPageIndexId': num-1,
                'submitTimeFrom': '{}'.format(start_time),
                'submitTimeTo': '{}'.format(end_time),
                "acceptance.contractTitle.contractName": "",
                "acceptance.result": "",
                "acceptance.contractTitle.planSno": "",
            }
        else:
            Dats = {
                'pageIndex': num,
                'pageSize': 15,
                'pointPageIndexId': num-1,
                'submitTimeFrom': '{}'.format(start_time),
                'submitTimeTo': '{}'.format(end_time),
                "prjReqQueryModel.buyerOrg.name": "",
                "prjReqQueryModel.proxyOrgNamee": "",
                "prjReqQueryModel.title": "",
                "prjReqQueryModel.webInfo.id": "",
            }
        datas = {**payloadData, **Dats}
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
            uls = soup.find("div", class_="m_m_cont").table
            if '没有数据' in uls.text.strip():
                return pd.DataFrame()
            lis = uls.find_all("tr")
            data = []
            for tr in lis[1:]:
                a = tr.find('a', class_='c_m_check')
                if 'queryPrjReqList.do' in tt_url:
                    name = tr.find_all('td')[3]['title']
                    ggstart_time = tr.find_all('td')[-3].text.strip()
                else:
                    name = tr.find_all('td')[1]['title']
                    ggstart_time = tr.find_all('td')[4].text.strip()
                href = a['href'].strip()
                if 'http' in href:
                    link = href
                else:
                    link = 'http://www.gdgpo.gov.cn' + href
                info = {}
                if 'queryAcceptanceList.do' in tt_url:
                    if tr.find_all('td')[2]:
                        xm_num = tr.find_all('td')[2]['title']
                        if xm_num:info['xm_num']=xm_num
                    if tr.find_all('td')[3]:
                        ht_time = tr.find_all('td')[3].text.strip()
                        if ht_time:info['ht_time']=ht_time
                    if tr.find_all('td')[5]:
                        ysr = tr.find_all('td')[5].text.strip()
                        if ysr:info['ysr']=ysr
                elif 'queryPrjReqList.do' in tt_url:
                    if tr.find_all('td')[1]:
                        cgr = tr.find_all('td')[1]['title']
                        if cgr:info['cgr']=cgr
                    if tr.find_all('td')[2]:
                        cgdljg = tr.find_all('td')[2].text.strip()
                        if cgdljg:info['cgdljg']=cgdljg
                    if tr.find_all('td')[-4]:
                        cgp = tr.find_all('td')[-4].text.strip()
                        if cgp:info['cgp']=cgp
                    if tr.find_all('td')[-2]:
                        menhu = tr.find_all('td')[-2].text.strip()
                        if menhu:info['menhu']=menhu
                else:
                    if tr.find_all('td')[2]:
                        xm_num = tr.find_all('td')[2].text.strip()
                        if xm_num: info['xm_num'] = xm_num
                    if tr.find_all('td')[3]:
                        ht_time = tr.find_all('td')[3].text.strip()
                        if ht_time: info['ht_time'] = ht_time
                    if tr.find_all('td')[-2]:
                        menhu = tr.find_all('td')[-2].text.strip()
                        if menhu: info['menhu'] = menhu
                if info:
                    info = json.dumps(info, ensure_ascii=False)
                else:
                    info = None
                tmp = [name, ggstart_time, link, info]
                data.append(tmp)
            df = pd.DataFrame(data=data)
            return df


def f1(driver, num):
    # n = 0
    url = driver.current_url
    if ('queryPlanList.do' in url) or ('queryCityPlanList.do' in url):
        n = 0
        while n < 6:
            try:
                time.sleep(2 * n)
                df = f1_data(driver, num)
                return df
            except:
                n += 1
    if ('queryAcceptanceList.do' in url) or ('queryCityAcceptanceList.do' in url) or ('queryPrjReqList.do' in url):
        n = 0
        while n < 6:
            # try:
            time.sleep(2 * n)
            df = f1_requests(driver, num)
            return df
            # except:
            #     n += 1



def f2(driver):
    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s' % proxy}
    except:
        proxies = {}
    global tt_url
    global payloadData
    url = driver.current_url
    if 'queryPrjReqList.do' in url:
        tt_url = ''
        tt_url = driver.current_url
        n = 0
        payloadData = {}
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

    else:
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
    if 'queryPlanList.do' in tt_url:
        Data = {
            'pageIndex': 1,
            'pageSize': 15,
            'pointPageIndexId': 1,
            'manOrgAnswerDateFrom': '{}'.format(start_time),
            'manOrgAnswerDateTo': '{}'.format(end_time),
            "levelStatus": "",
            "planContent.auditNumber": "",
            "planContent.demandDate3": "",
            "planContent.govBuyServiceContent": "",
            "planContent.govBuyServiceType": "",
            "planContent.pppPlankType": "",
            "planContent.projectName": "",
            "planContent.stockIndexName": "",
            "planContent.unitOrg.name": "",
            "regionCode": "",
        }

    elif 'queryCityPlanList.do' in tt_url:
        Data = {
            'pageIndex': 1,
            'pageSize': 15,
            'pointPageIndexId': 1,
            'manOrgAnswerDateFrom': '{}'.format(start_time),
            'manOrgAnswerDateTo': '{}'.format(end_time),
            "planContent.auditNumber": "",
            "planContent.demandDate3": "",
            "planContent.govBuyServiceContent": "",
            "planContent.govBuyServiceType": "",
            "planContent.pppPlankType": "",
            "planContent.projectName": "",
            "planContent.stockIndexName": "",
            "planContent.stockType.id": "",
            "planContent.unitOrg.name": "",
            "siteCode": "",
        }

    elif 'queryAcceptanceList.do' in tt_url:
        Data = {
            'pageIndex': 1,
            'pageSize': 15,
            'pointPageIndexId': 1,
            'submitTimeFrom': '{}'.format(start_time),
            'submitTimeTo': '{}'.format(end_time),
            "acceptance.contractTitle.contractName": "",
            "acceptance.operator": "",
            "acceptance.result": "",
            "acceptance.contractTitle.planSno": "",
        }

    elif 'queryCityAcceptanceList.do' in tt_url:
        Data = {
            'pageIndex': 1,
            'pageSize': 15,
            'pointPageIndexId': 1,
            'submitTimeFrom': '{}'.format(start_time),
            'submitTimeTo': '{}'.format(end_time),
            "acceptance.contractTitle.contractName": "",
            "acceptance.result": "",
            "acceptance.contractTitle.planSno": "",
        }
    else:
        Data = {
            'pageIndex': 1,
            'pageSize': 15,
            'pointPageIndexId': 1,
            'submitTimeFrom': '{}'.format(start_time),
            'submitTimeTo': '{}'.format(end_time),
            "prjReqQueryModel.buyerOrg.name": "",
            "prjReqQueryModel.proxyOrgNamee": "",
            "prjReqQueryModel.title": "",
            "prjReqQueryModel.webInfo.id": "",
        }
    datas = {**Data, **payloadData}
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
        uls = soup.find("div", class_="m_m_cont").table
        if '没有数据' in uls.text.strip():
            return 0
        if uls.find('a', class_='c_m_check')== None:
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

    sitewebId = OrderedDict([("省直", "4028889705bebb510105bec068b00003"),
                           ("佛山市", "4028889705bebb510105bec1f8670004"),
                           ("梅州市", "4028889705bedd7e0105beec36890004"),
                           ("河源市", "4028889705bedd7e0105beed4b240005"),
                           ("阳江市", "4028889705bedd7e0105bef239d20006"),
                           ("清远市", "4028889705bedd7e0105bef333260007"),
                           ("东莞市", "4028889705bedd7e0105bef45f220008"),
                           ("中山市", "4028889705bedd7e0105bef51d7f0009"),
                           ("揭阳市", "4028889705bedd7e0105bef673b8000b"),
                           ("云浮市", "4028889705bedd7e0105bef70a69000c"),
                           ("汕头市", "4028889705bebb510105becdbed40009"),
                           ("江门市", "4028889705bebb510105becf79c2000a"),
                           ("湛江市", "4028889705bebb510105bed04b88000b"),
                           ("茂名市", "4028889705bebb510105bed1471d000c"),
                           ("广州市", "4028889705bebb510105bec9f3490006"),
                           ("肇庆市", "4028889705bebb510105bed24c86000d"),
                           ("潮州市", "4028889705bedd7e0105bef5da47000a"),
                           ("深圳市", "4028889705bebb510105becb72d30007"),
                           ("汕尾市", "4028889705bebb510105bed6e6ac000f"),
                           ("惠州市", "4028889705bebb510105bed2e21f000e"),
                           ("韶关市", "4028889705bebb510105becc5dbf0008"),
                           ("珠海市", "4028889705bebb510105bec522060005"),
                            ])

    regionIds = OrderedDict([("省直", "01"),
                             ("佛山市", "0105"), ("梅州市", "0108"), ("河源市", "0107"), ("阳江市", "0114"), ("清远市", "0118"),
                             ("东莞市", "0111"), ("中山市", "0112"), ("揭阳市", "0120"), ("云浮市", "0121"), ("汕头市", "0104"),
                             ("江门市", "0113"), ("湛江市", "0115"), ("茂名市", "0116"), ("广州市", "0101"), ("肇庆市", "0117"),
                             ("潮州市", "0119"), ("深圳市", "0102"), ("汕尾市", "0110"), ("惠州市", "0109"), ("韶关市", "0106"), ("珠海市", "0103")
                             ])

    noticeTypeId = OrderedDict([("协议采购", "297e6a6a4a0653f4014a0a31ee5e4158"),
                           ("网上竞价", "297e6a6a4a0653f4014a0a321b37415a"),
                           ("自主采购", "297e6a6a4a0653f4014a0a3251644160"),
                           ("批量采购", "297e6a6a4a78197c014a781c539c0000"),
                           ("电商直购", "297e6a6a4da3e22e014da7ef5fa802bb"),
                           ("竞争性磋商", "40288ba84fbd5791014fc9ce54703966"),
                           ("定点采购", "40288ba85958f3f701595907a57f004c"),
                           ("单一来源采购", "402888a405b8f7460105bcfd5bd80007"),
                           ("公开招标", "402888a405bd3b020105bd3c1c1d0001"),
                           ("询价采购", "4028889705c927090105c93ccc820003"),
                           ("竞争性谈判采购", "4028889705c927090105c93cfd850004"),
                           ("邀请招标", "402888a405c7baab0105c7bd419f0003"),
                           ("其它采购方式", "8a90b3a907124a230107126f96d30004"),
                           ("教育部门协议采购", "40288ba85047360d01504c1670b35e11"),

                            ])

    # 省级验收公告
    for w1 in sitewebId.keys():
        p1 = sitewebId[w1]
        p2 = regionIds[w1]
        href = "http://www.gdgpo.gov.cn/queryAcceptanceList.do&sitewebId=%s&webInfo.id=%s" % (p1, p2)
        tb = "zfcg_yanshou_sj_diqu%s_gg" % (p2)
        col = ["name", "ggstart_time", "href", "info"]
        tmp = [tb, href, col, add_info(f1, {"diqu1": w1}), f2]
        data.append(tmp)

    # 市县验收公告
    for w1 in sitewebId.keys():
        p1 = sitewebId[w1]
        p2 = regionIds[w1]
        href = "http://www.gdgpo.gov.cn/queryCityAcceptanceList.do&sitewebId=%s&webInfo.id=%s" % (p1, p2)
        tb = "zfcg_yanshou_sx_diqu%s_gg" % (p2)
        col = ["name", "ggstart_time", "href", "info"]
        tmp = [tb, href, col, add_info(f1, {"diqu1": w1}), f2]
        data.append(tmp)

    # 省级采购计划
    k = 0
    for w1 in noticeTypeId.keys():
        k+=1
        p1 = noticeTypeId[w1]
        href = "http://www.gdgpo.gov.cn/queryPlanList.do&planContent.stockType.id=%s" % (p1)
        tb = "zfcg_gqita_cgjh_sj_zblx%d_gg" % (k)
        col = ["name", "ggstart_time", "href", "info"]
        tmp = [tb, href, col, add_info(f1, {"zblx": w1}), f2]
        data.append(tmp)

    # 市县采购计划
    for w1 in sitewebId.keys():
        p1 = sitewebId[w1]
        p2 = regionIds[w1]
        href = "http://www.gdgpo.gov.cn/queryCityPlanList.do&sitewebId=%s" % (p1)
        tb = "zfcg_gqita_cgjh_sx_diqu%s_gg" % (p2)
        col = ["name", "ggstart_time", "href", "info"]
        tmp = [tb, href, col, add_info(f1, {"diqu1": w1}), f2]
        data.append(tmp)


    data1 = data.copy()
    remove_arr = []
    for w in data:
        if w[0] in remove_arr: data1.remove(w)
    return data1
    # 创建data

data = get_data()


data1 = [
    ["zfcg_yucai_gg", "http://www.gdgpo.gov.cn/queryPrjReqList.do",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]

data.extend(data1)



##广东省政府采购网,中国政府采购网广东分网,验收,预采,采购计划
def work(conp, **args):
    est_meta_large(conp, data=data, diqu="广东省", **args)
    est_html(conp, f=f3, **args)


# 修改日期：2019/7/24
# 页数太多，跑不完，总是会跳回首页，详情页加载慢
if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "guoziqiang", "guangdong"],pageloadtimeout=120,interval_page=100,num=45)

    # for d in data[2:]:
    #     url=d[1]
    #     if 'queryCityAcceptanceList.do' in url and '4028889705bedd7e0105beec36890004' in url :
    #         print(url)
    #         driver = webdriver.Chrome()
    #         driver.get(url)
    #         df = f2(driver)
    #         print(df)
    #         driver = webdriver.Chrome()
    #         driver.get(url)
    #
    #         df=f1(driver, 12)
    #         print(df.values)
    #         for f in df[2].values:
    #             d = f3(driver, f)
    #             print(d)