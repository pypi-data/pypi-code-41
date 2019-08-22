import json
import math
import time

import pandas as pd
import re
import requests

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from zlsrc.util.etl import  est_meta, est_html, add_info
from zlsrc.util.fake_useragent import UserAgent
ua=UserAgent()



def f1(driver, num):

    try:
        proxies_data = webdriver.DesiredCapabilities.CHROME
        proxies_chromeOptions = proxies_data['goog:chromeOptions']['args']
        proxy = proxies_chromeOptions[0].split('=')[1]
        proxies = {'http': '%s' % proxy}
    except:
        proxies={}

    headers = {
        "User-Agent": ua.chrome,
    }

    locator = (By.XPATH, "//body/pre[string-length()>200]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    # cnum = int(re.findall(r'&pageIndex=(\d+)&', url)[0])


    # if num != cnum:
    #     url = re.sub(r"&pageIndex=\d+&", "&pageIndex=%s&" % num, url)
    #
    #     val = len(driver.page_source)
    #
    #     driver.get(url)
    #     locator = (By.XPATH, "//body/pre[string-length()>200]")
    #
    #     WebDriverWait(
    #         driver, 10).until(
    #         lambda driver: len(driver.page_source) != val and EC.presence_of_element_located(locator))
    #     time.sleep(0.5)

    data = []
    url = re.sub(r"&pageIndex=\d+&", "&pageIndex=%s&" % num, url)
    res = requests.get(url,headers=headers,proxies=proxies,timeout=40)
    content=res.content.decode('unicode_escape')

    contents=re.findall('"custom":"\[\{(.+)\}\]"',content)[0]
    cons=re.findall('\{(.+?)\}',contents)
    for c in cons:

        name=re.findall('"title":"(.+?)"',c)[0]
        ggstart_time=re.findall('"infodate":"(.+?)"',c)[0]
        categorynum=re.findall('"categorynum":"(.+?)"',c)[0]
        href=re.findall('"infoid":"(.+?)"',c)[0]
        diqu=re.findall('"infoC":"(.+?)"',c)

        diqu=diqu[0] if diqu else None

        info = json.dumps({'diqu':diqu},ensure_ascii=False)
        href="opendetail('%s','%s')"%(href,categorynum)
        tmp = [name, ggstart_time, href,info]
        # print(tmp)
        data.append(tmp)

    df = pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.XPATH, "//body/pre[string-length()>200]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    url=driver.current_url

    url=re.sub('cmd=getInfoList&pageIndex=\d+&pageSize=\d+&','cmd=getInfoListCount&',url)
    driver.get(url)
    locator = (By.XPATH, "//body/pre[contains(string(),'custom')]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    total=driver.find_element_by_xpath('//body/pre').text
    # print(total)
    total=re.findall('"custom":"(\d+)"',total)[0]

    total=math.ceil(int(total)/18)

    driver.quit()
    return total


def f3(driver, url):

    curl=driver.current_url

    if curl != 'https://www.cqggzy.com/jyxx/jyxx-page.html':
        driver.get("https://www.cqggzy.com/jyxx/jyxx-page.html")

    locator = (By.XPATH, '//table[@class="list-tbnew"]//tr[2]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    driver.execute_script(url)
    handles=driver.window_handles
    driver.switch_to.window(handles[-1])
    locator = (By.XPATH, '//div[@class="detail-block"][string-length()>50]')
    WebDriverWait(
        driver, 10).until(
        EC.presence_of_all_elements_located(locator))

    before = len(driver.page_source)
    time.sleep(0.1)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(0.1)
        after = len(driver.page_source)
        i += 1
        if i > 5:
            break

    page = driver.page_source

    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', class_='detail-block')

    driver.close()
    driver.switch_to.window(handles[0])

    return div


data = [
    ["gcjs_zhaobiao_gg",
     "https://www.cqggzy.com/EpointWebBuilderService/getInfoListAndCategoryList.action?cmd=getInfoList&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014001001&title=&infoC=",
     ["name", "ggstart_time", "href", 'info'], f1, f2],

    ["gcjs_zhaobiao_yaoqing_gg",
     "https://www.cqggzy.com/EpointWebBuilderService/getInfoListAndCategoryList.action?cmd=getInfoList&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014001014&title=&infoC=",
     ["name", "ggstart_time", "href", 'info'], add_info(f1,{"zbfs":'邀请招标'}), f2],

    ["gcjs_gqita_da_bian_gg",
     "https://www.cqggzy.com/EpointWebBuilderService/getInfoListAndCategoryList.action?cmd=getInfoList&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014001002&title=&infoC=",
     ["name", "ggstart_time", "href", 'info'], f1, f2],

   [ "gcjs_gqita_richeng_gg",
     "https://www.cqggzy.com/EpointWebBuilderService/getInfoListAndCategoryList.action?cmd=getInfoList&pageIndex=2&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014001015&title=&infoC=",
     ["name", "ggstart_time", "href", 'info'], add_info(f1,{"jytype":'日程安排'}), f2],

    ["gcjs_zhongbiaohx_gg",
     "https://www.cqggzy.com/EpointWebBuilderService/getInfoListAndCategoryList.action?cmd=getInfoList&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014001003&title=&infoC=",
     ["name", "ggstart_time", "href", 'info'], f1, f2],
    ["gcjs_zhongbiao_gg",
     "https://www.cqggzy.com/EpointWebBuilderService/getInfoListAndCategoryList.action?cmd=getInfoList&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014001004&title=&infoC=",
     ["name", "ggstart_time", "href", 'info'], f1, f2],
    ["gcjs_liubiao_gg",
     "https://www.cqggzy.com/EpointWebBuilderService/getInfoListAndCategoryList.action?cmd=getInfoList&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014001016&title=&infoC=",
     ["name", "ggstart_time", "href", 'info'], f1, f2],

    ["zfcg_zhaobiao_gg",
     "https://www.cqggzy.com/EpointWebBuilderService/getInfoListAndCategoryList.action?cmd=getInfoList&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014005001&title=&infoC=",
     ["name", "ggstart_time", "href", 'info'], f1, f2],
    ["zfcg_gqita_da_bian_gg",
     "https://www.cqggzy.com/EpointWebBuilderService/getInfoListAndCategoryList.action?cmd=getInfoList&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014005002&title=&infoC=",
     ["name", "ggstart_time", "href", 'info'], f1, f2],
    ["zfcg_zhongbiaohx_gg",
     "https://www.cqggzy.com/EpointWebBuilderService/getInfoListAndCategoryList.action?cmd=getInfoList&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014005003&title=&infoC=",
     ["name", "ggstart_time", "href", 'info'], f1, f2],
    ["zfcg_zhongbiao_gg",
     "https://www.cqggzy.com/EpointWebBuilderService/getInfoListAndCategoryList.action?cmd=getInfoList&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014005004&title=&infoC=",
     ["name", "ggstart_time", "href", 'info'], f1, f2],
    ["zfcg_yucai_gg",
     "https://www.cqggzy.com/EpointWebBuilderService/getInfoListAndCategoryList.action?cmd=getInfoList&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014005008&title=&infoC=",
     ["name", "ggstart_time", "href", 'info'], f1, f2],

    ["qsy_zhaobiao_gg",
     "https://www.cqggzy.com/EpointWebBuilderService/getInfoListAndCategoryList.action?cmd=getInfoList&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014008001&title=&infoC=",
     ["name", "ggstart_time", "href", 'info'], f1, f2],
    ["qsy_gqita_da_bian_gg",
     "https://www.cqggzy.com/EpointWebBuilderService/getInfoListAndCategoryList.action?cmd=getInfoList&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014008002&title=&infoC=",
     ["name", "ggstart_time", "href", 'info'], f1, f2],
    ["qsy_zhongbiaohx_gg",
     "https://www.cqggzy.com/EpointWebBuilderService/getInfoListAndCategoryList.action?cmd=getInfoList&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014008003&title=&infoC=",
     ["name", "ggstart_time", "href", 'info'], f1, f2],

    ["jqita_zhaobiao_gg",
     "https://www.cqggzy.com/EpointWebBuilderService/getInfoListAndCategoryList.action?cmd=getInfoList&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014003001&title=&infoC=",
     ["name", "ggstart_time", "href", 'info'], add_info(f1,{'tag':'机电设备'}), f2],
    ["jqita_gqita_da_bian_gg",
     "https://www.cqggzy.com/EpointWebBuilderService/getInfoListAndCategoryList.action?cmd=getInfoList&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014003002&title=&infoC=",
     ["name", "ggstart_time", "href", 'info'], add_info(f1,{'tag':'机电设备'}), f2],
    ["jqita_zhongbiao_gg",
     "https://www.cqggzy.com/EpointWebBuilderService/getInfoListAndCategoryList.action?cmd=getInfoList&pageIndex=1&pageSize=18&siteguid=d7878853-1c74-4913-ab15-1d72b70ff5e7&categorynum=014003004&title=&infoC=",
     ["name", "ggstart_time", "href", 'info'], add_info(f1,{'tag':'机电设备'}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="重庆市", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':

    conp = ["postgres", "since2015", "192.168.3.171", "chongqing", "chongqing"]

    # work(conp=conp,num=1,total=2,headless=True,ipNum=0)

    urllist=["opendetail('14a54184-ca29-4510-b22d-d6d4c5ab6a7f','014001001002')",
             "opendetail('b0c2bfa5-d9ea-4535-863c-197c646d98c8','014001001002')",
             "opendetail('0fd25bf1-4782-4fa7-953c-fda46505a7fc','014001001002')",
             "opendetail('eb17085c-a42b-498e-b58a-b091a33d1ce6','014001001002')",
             "opendetail('f0308030-aef8-4759-a869-9549ae773c21','014001001010')",
             "opendetail('55917e6f-5a44-49e5-8466-55eaf479a952','014001001010')",
             "opendetail('4dca951e-549c-46f1-9189-abd64eaf7940','014001001001')",
             "opendetail('272e162d-a2f7-493b-ae73-25d8469355be','014001001010')",
             "opendetail('bdb1371f-c77c-43d3-ad54-90ba93c3438e','014001001002')",
             "opendetail('736b2f60-926f-4c83-a223-71ca786af47f','014001001001')",
             ]
    driver=webdriver.Chrome()
    for url in urllist:
        f3(driver,url)