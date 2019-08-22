import json
import time

import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from zlsrc.util.etl import est_tbs, est_meta, est_html



def f1(driver,num):
    locator = (By.XPATH, '//pre[string-length()>100][contains(string(),"total")]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    url_1 =driver.current_url
    cnum=re.findall('&page=(\d+?)&',url_1)[0]
    if int(cnum) != num:
        page_count=len(driver.page_source)
        val = re.findall('"gongShiGuid":"(.+?)"',driver.page_source)[1]
        url_2=re.sub('(?<=&page=)\d+',str(num),url_1)
        driver.get(url_2)

        locator = (By.XPATH, '//pre[not(contains(string(),"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        WebDriverWait(driver,10).until(lambda driver:len(driver.page_source) != page_count)

    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.find('pre').get_text()

    contents=json.loads(content)['rows']
    for c in contents:

        name=c.get('title')
        bianhao=c.get('bianHao')
        gclx=c.get('gongChengLeiBieText')
        xmlx=c.get('gongChengTypeText')
        ggstart_time=c.get('faBuStartTimeText')
        gongShiType=c.get('gongShiType')
        cgptflag=c.get('cgptflag')
        fromType=c.get('fromType')
        yxtid=c.get('yuanXiTongId')



        if fromType == 2:

            if gongShiType == 10:
                url = "/jiaoyixingxi/zbgg_view.html?guid="+yxtid
            elif gongShiType == 170:
                url = "/jiaoyixingxi/bggs_view.html?guid="+yxtid
            elif gongShiType == 'kzj':
                url = "/jiaoyixingxi/kzjgs_view.html?guid="+yxtid
            elif gongShiType == 180:
                url = "/jiaoyixingxi/pbjg_view.html?guid="+yxtid
            elif gongShiType == 50:
                url = "/jiaoyixingxi/zbgs_view.html?guid="+yxtid

            elif gongShiType == 130:
                url = "/jiaoyixingxi/ycxx_view.html?guid="+yxtid
            else:
                url = "/jiaoyixingxi/zbsb_view.html?guid="+yxtid
        else :
            if gongShiType == 70:
                if cgptflag and cgptflag != "0":
                    if cgptflag == "1":
                        url = "http://www.ezggzy.cn/zcsc/wssc/caiGouXinXi/toJingJiaBulletenDetail.html?guid=" + yxtid
                    elif cgptflag == "2":
                        url = "http://www.ezggzy.cn/zcsc/wssc/caiGouXinXi/toZhiGouBulletenDetail.html?guid=" + yxtid

                else:
                    url = "/jiaoyizfcg/zbgg_view.html?guid=" + yxtid

            elif gongShiType == 170:
                if cgptflag and cgptflag != "0":
                    if cgptflag == "5":
                        url = "http://www.ezggzy.cn/zcsc/wssc/caiGouXinXi/toBuYiBulletenDetail.html?guid=" + yxtid

                else:
                    url = "/jiaoyizfcg/bggs_view.html?guid=" + yxtid

            elif gongShiType == 50:
                if cgptflag and cgptflag != "0":
                    if cgptflag == "3":
                        url = "http://www.ezggzy.cn/zcsc/wssc/caiGouXinXi/toJingJiaResultDetail.html?guid=" + yxtid
                    elif cgptflag == "4":
                        url = "http://www.ezggzy.cn/zcsc/wssc/caiGouXinXi/toZhiGouResultDetail.html?guid=" + yxtid

                else:
                    url = "/jiaoyizfcg/zbgs_view.html?guid=" + yxtid
            else:
                url='空'
        url='http://ggzyj.ezhou.gov.cn'+url

        if fromType == 2:
            info=json.dumps({'biaohao':bianhao,'gclx':gclx,'xmlx':xmlx},ensure_ascii=False)
        else:
            info=json.dumps({'xmlx':xmlx},ensure_ascii=False)

        tmp = [name, url,ggstart_time,info]

        data.append(tmp)

    df=pd.DataFrame(data=data)

    return df


def f2(driver):
    locator = (By.XPATH, '//pre[string-length()>100][contains(string(),"total")]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    page = re.findall('"totalPage":(\d+)',driver.page_source)[0]
    total = int(page)
    driver.quit()
    return total

def f3(driver, url):
    driver.get(url)
    try:
        locator = (By.XPATH, '//div[@class="con"][string-length()>100] | //div[@class="content_nr"][string-length()>100]')
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
        flag = 1
    except:
        locator = (By.XPATH, '//div[@class="xmmc_bt"][string-length()>100]')
        WebDriverWait(driver, 1).until(EC.presence_of_all_elements_located(locator))
        flag = 2

    before = len(driver.page_source)
    time.sleep(0.1)
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
    if flag == 1:
        div = soup.find('div',class_="xmmc_bt")
        if div == None:
            div = soup.find('div',class_="content_nr")
    elif flag == 2:
        div = soup.find('div', class_='xmmc_bt')
    else:raise ValueError

    if div == None:
        raise ValueError('div is None')

    return div

data=[
    #
    ["gcjs_zhaobiao_gg","http://ggzyj.ezhou.gov.cn/jiaoyixinxi/queryJiaoYiXinXiPagination.do?bianHao=&gongChengLeiBie=&gongChengType=&gongShiType=10&page=1&rows=15&title=&type=10",[ "name", "href", "ggstart_time", "info"],f1,f2],
    ["gcjs_gqita_da_bian_gg","http://ggzyj.ezhou.gov.cn/jiaoyixinxi/queryJiaoYiXinXiPagination.do?bianHao=&gongChengLeiBie=&gongChengType=&gongShiType=170&page=1&rows=15&title=&type=10",[ "name", "href", "ggstart_time", "info"],f1,f2],
    ["gcjs_zhongbiaohx_gg","http://ggzyj.ezhou.gov.cn/jiaoyixinxi/queryJiaoYiXinXiPagination.do?bianHao=&gongChengLeiBie=&gongChengType=&gongShiType=180&page=1&rows=15&title=&type=10",[ "name", "href", "ggstart_time", "info"],f1,f2],
    ["gcjs_zhongbiao_gg","http://ggzyj.ezhou.gov.cn/jiaoyixinxi/queryJiaoYiXinXiPagination.do?bianHao=&gongChengLeiBie=&gongChengType=&gongShiType=50&page=1&rows=15&title=&type=10",[ "name", "href", "ggstart_time", "info"],f1,f2],
    ["gcjs_liubiao_gg","http://ggzyj.ezhou.gov.cn/jiaoyixinxi/queryJiaoYiXinXiPagination.do?bianHao=&gongChengLeiBie=&gongChengType=&gongShiType=130&page=1&rows=15&title=&type=10",[ "name", "href", "ggstart_time", "info"],f1,f2],

    ["zfcg_zhaobiao_gg","http://ggzyj.ezhou.gov.cn/jiaoyixinxi/queryJiaoYiXinXiPagination.do?bianHao=&gongChengLeiBie=&gongChengType=&gongShiType=70&page=1&rows=15&title=&type=20",[ "name", "href", "ggstart_time", "info"],f1,f2],
    ["zfcg_gqita_da_bain_gg","http://ggzyj.ezhou.gov.cn/jiaoyixinxi/queryJiaoYiXinXiPagination.do?bianHao=&gongChengLeiBie=&gongChengType=&gongShiType=170&page=1&rows=15&title=&type=20",[ "name", "href", "ggstart_time", "info"],f1,f2],
    ["zfcg_zhongbiao_gg","http://ggzyj.ezhou.gov.cn/jiaoyixinxi/queryJiaoYiXinXiPagination.do?bianHao=&gongChengLeiBie=&gongChengType=&gongShiType=50&page=1&rows=15&title=&type=20",[ "name", "href", "ggstart_time", "info"],f1,f2],
    ["zfcg_liubiao_gg","http://ggzyj.ezhou.gov.cn/jiaoyixinxi/queryJiaoYiXinXiPagination.do?bianHao=&gongChengLeiBie=&gongChengType=&gongShiType=130&page=1&rows=15&title=&type=20",[ "name", "href", "ggstart_time", "info"],f1,f2],


]

def work(conp,**args):
    est_meta(conp,data=data,diqu="湖北省鄂州市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':

    conp=["postgres","since2015","192.168.3.171","lchest","hubei_ezhou"]

    work(conp=conp,total=2,num=1)

    # driver = webdriver.Chrome()
    # dff = f3(driver, 'http://ggzyj.ezhou.gov.cn/jiaoyizfcg/zbgs_view.html?guid=0e47d201-4b4b-4e87-b726-069a0d073cad')
    # print(dff)