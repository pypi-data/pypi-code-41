import math
import pandas as pd
import re
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from zlsrc.util.etl import add_info,est_meta,est_html,est_tbs



tt = None

def f1(driver, num):
    locator = (By.XPATH, "//pre[string-length()>100]")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = int(re.findall(r'page=(\d+)', url)[0])
    if num != cnum:
        pre1 = driver.find_element_by_xpath("//pre").text.strip()
        datas1 = json.loads(pre1)
        rows1 = datas1['json'][tt]['tp'][0]
        val1 = rows1['id']
        s = 'page=%d' % num if num>1 else 'page=1'
        url = re.sub('page=[0-9]+', s, url)
        driver.get(url)
        time.sleep(1)
        locator = (By.XPATH, "//pre[string-length()>100]")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
        pre2 = driver.find_element_by_xpath("//pre").text.strip()
        datas2 = json.loads(pre2)
        rows2 = datas2['json'][tt]['tp'][0]
        val2 = rows2['id']
        if val1 == val2:
            raise ValueError
    data = []
    pre = driver.find_element_by_xpath("//pre").text.strip()
    datas = json.loads(pre)
    rows = datas['json'][tt]['tp']
    for tr in rows:
        info = {}
        # gcjs
        if tt == 'tp':
            name = tr['Title']
            ggstart_time = tr['publishTime']
            href = 'http://www.syx.gov.cn/ztbw/fjebid/jypt.html?type=招标公告&tpid='+tr['id']+'&tpTitle='+name
            gclx = tr['type']
            if gclx:info['gclx']=gclx
            lx = tr['Category']
            if lx:info['lx'] = lx
            if info:info = json.dumps(info, ensure_ascii=False)
            else:info = None
            tmp = [name, ggstart_time, href, info]
            data.append(tmp)
        elif tt == 'bid':
            name = tr['Title']
            ggstart_time = tr['publishTime']
            href = 'http://www.syx.gov.cn/ztbw/fjebid/jypt.html?type=中标公示&tpid='+tr['TpId']+'&tpTitle='+name
            gclx = tr['type']
            if gclx:info['gclx']=gclx
            lx = tr['Category']
            if lx:info['lx'] = lx
            if info:info = json.dumps(info, ensure_ascii=False)
            else:info = None
            tmp = [name, ggstart_time, href, info]
            data.append(tmp)
        elif tt == 'sup':
            name = tr['Title']
            ggstart_time = tr['publishTime']
            href = 'http://www.syx.gov.cn/ztbw/fjebid/jypt.html?type=补充通知&tpid='+tr['TpId']+'&tpTitle='+name
            lx = tr['Category']
            if lx:info['lx'] = lx
            if info:info = json.dumps(info, ensure_ascii=False)
            else:info = None
            tmp = [name, ggstart_time, href, info]
            data.append(tmp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    global tt
    url = driver.current_url
    tt = url.rsplit('&', maxsplit=1)[1]
    surl = url.rsplit('&', maxsplit=1)[0]
    # print(surl)
    driver.get(surl)
    locator = (By.XPATH, "//pre[string-length()>100]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    pre = driver.find_element_by_xpath("//pre").text.strip()
    datas = json.loads(pre)
    total = datas['json'][tt]['total']
    num = math.ceil(int(total)/10)
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//iframe[@id='myFrame']")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    driver.switch_to_frame('myFrame')
    locator = (By.XPATH, "//body[string-length()>140]")
    WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located(locator))
    before = len(driver.page_source)
    time.sleep(0.5)
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
    div = soup.find('body')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://www.syx.gov.cn/ztbw/TenderProject/ListAll?page=1&records=10&category=%E6%88%BF%E5%B1%8B%E5%B8%82%E6%94%BF%2C%E6%B0%B4%E5%88%A9%E5%B7%A5%E7%A8%8B%2C%E4%BA%A4%E9%80%9A%E8%BF%90%E8%BE%93%2C%E5%9C%9F%E5%9C%B0%E5%B9%B3%E6%95%B4%2C%E5%85%B6%E4%BB%96%E8%A1%8C%E4%B8%9A&title=&tp",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_gqita_bian_bu_gg",
     "http://www.syx.gov.cn/ztbw/TenderProject/ListAll?page=1&records=10&category=%E6%88%BF%E5%B1%8B%E5%B8%82%E6%94%BF%2C%E6%B0%B4%E5%88%A9%E5%B7%A5%E7%A8%8B%2C%E4%BA%A4%E9%80%9A%E8%BF%90%E8%BE%93%2C%E5%9C%9F%E5%9C%B0%E5%B9%B3%E6%95%B4%2C%E5%85%B6%E4%BB%96%E8%A1%8C%E4%B8%9A&title=&sup",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiaohx_gg",
     "http://www.syx.gov.cn/ztbw/TenderProject/ListAll?page=1&records=10&category=%E6%88%BF%E5%B1%8B%E5%B8%82%E6%94%BF%2C%E6%B0%B4%E5%88%A9%E5%B7%A5%E7%A8%8B%2C%E4%BA%A4%E9%80%9A%E8%BF%90%E8%BE%93%2C%E5%9C%9F%E5%9C%B0%E5%B9%B3%E6%95%B4%2C%E5%85%B6%E4%BB%96%E8%A1%8C%E4%B8%9A&title=&bid",
     ["name", "ggstart_time", "href", "info"], f1, f2],


###
    ["zfcg_zhaobiao_gg",
     "http://www.syx.gov.cn/ztbw/TenderProject/ListAll?page=1&records=10&category=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&title=&tp",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_gqita_bian_bu_gg",
     "http://www.syx.gov.cn/ztbw/TenderProject/ListAll?page=1&records=10&category=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&title=&sup",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhongbiao_gg",
     "http://www.syx.gov.cn/ztbw/TenderProject/ListAll?page=1&records=10&category=%E6%94%BF%E5%BA%9C%E9%87%87%E8%B4%AD&title=&bid",
     ["name", "ggstart_time", "href", "info"], f1, f2],
]


def work(conp,**args):
    est_meta(conp,data=data,diqu="湖南省邵阳市邵阳县",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","zlsrc","shaoyangxian"])

    # for d in data[2:]:
    #     driver=webdriver.Chrome()
    #     url=d[1]
    #     print(url)
    #     driver.get(url)
    #     df = f2(driver)
    #     print(df)
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #
    #     df=f1(driver, 3)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)

