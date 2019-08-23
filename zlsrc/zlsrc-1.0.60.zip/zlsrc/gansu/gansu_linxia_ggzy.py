import json
import pandas as pd
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
from zlsrc.util.etl import  est_meta, est_html
from zlsrc.util.etl import add_info



def f1(driver, num):
    locator = (By.XPATH, '//dl[@class="byTradingDetailParent clear"][1]//a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, '//li[@class="paginate_button active"]/a')
    cnum = int(WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text)

    if num != cnum:
        page_count = len(driver.page_source)
        val = driver.find_element_by_xpath('//dl[@class="byTradingDetailParent clear"][1]//a').get_attribute('href')[-25:]

        driver.execute_script("page(%s,20,'');" % num)

        locator = (By.XPATH, "//dl[@class='byTradingDetailParent clear'][1]//a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        WebDriverWait(driver, 10).until(lambda driver: len(driver.page_source) != page_count)
    page = driver.page_source

    soup = BeautifulSoup(page, "html.parser")

    dls = soup.find_all("dl", class_="byTradingDetailParent clear")

    data = []

    for dl in dls:
        name = dl.find("a").get_text().strip()
        href = dl.find("a")['href']
        ggstart_time = dl.find("span",class_='byTradingDetailTime').text.strip()
        href ='http://www.lxggzyjy.com'+ href

        if dl.find('ul',class_='clear'):
            tag=dl.find('ul',class_='clear').get_text().replace('\n',' ')
            info=json.dumps({'tag':tag},ensure_ascii=False)
        else:info=None
        tmp = [name, ggstart_time, href,info]

        data.append(tmp)

    df = pd.DataFrame(data=data)

    return df



def f2(driver):
    locator = (By.XPATH, '//dl[@class="byTradingDetailParent clear"][1]//a')
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    locator = (By.XPATH, '//ul[@class="pagination pagination-outline"]')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    try:
        total=driver.find_element_by_xpath('//li[@class="paginate_button next"][last()]/a').get_attribute('onclick')
        total=re.findall('page\((\d+),\d+',total)[0]
    except:
        total=1

    driver.quit()
    return int(total)


def chang_type(f):
    def inner(*args):
        driver=args[0]
        locator = (By.XPATH, '//dl[@class="byTradingDetailParent clear"][1]//a')
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        ctext=driver.find_element_by_xpath('//li[@class="byTradingList_NavActive"]').text
        if ctext == '招标公告':
            page_count = len(driver.page_source)

            driver.find_element_by_xpath('//div[@class="byTradingList_Nav"]//li[3]').click()

            WebDriverWait(driver, 10).until(lambda driver: len(driver.page_source) != page_count)
        return f(*args)
    return inner




def f3(driver, url):
    driver.get(url)

    locator = (By.XPATH, '//div[@class="jxTradingPublic"][string-length()>100] | //div[@class="yAnnounceLayer"][string-length()>100]')

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

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

    div = soup.find('div', class_='jxTradingMainLayer clear')
    if div == None:
        div = soup.find('div', id="content")
    if div == None:
        raise  ValueError

    return div


data=[
["gcjs_zhaobiao_jiaotong_gg",'http://www.lxggzyjy.com/f/newtrade/annogoods/list?selectedProjectType=3',["name","ggstart_time","href","info"],add_info(f1,{"gclx":"交通工程"}),f2],
["gcjs_zhongbiao_jiaotong_gg",'http://www.lxggzyjy.com/f/newtrade/annogoods/list?selectedProjectType=3',["name","ggstart_time","href","info"],chang_type(add_info(f1,{"gclx":"交通工程"})),chang_type(f2)],

["gcjs_zhaobiao_jiaotong_old_gg",'http://www.lxggzyjy.com/f/trade/annogoods/list?tradeStatus=1&selectedProjectType=A02',["name","ggstart_time","href","info"],add_info(f1,{"gclx":"交通工程"}),f2],
["gcjs_zhongbiao_jiaotong_old_gg",'http://www.lxggzyjy.com/f/trade/annogoods/list?tradeStatus=1&selectedProjectType=A02',["name","ggstart_time","href","info"],chang_type(add_info(f1,{"gclx":"交通工程"})),chang_type(f2)],

["gcjs_zhaobiao_fangjian_gg",'http://www.lxggzyjy.com/f/newtrade/annogoods/list?selectedProjectType=1',["name","ggstart_time","href","info"],add_info(f1,{"gclx":"房建市政"}),f2],
["gcjs_zhongbiao_fangjian_gg",'http://www.lxggzyjy.com/f/newtrade/annogoods/list?selectedProjectType=1',["name","ggstart_time","href","info"],chang_type(add_info(f1,{"gclx":"房建市政"})),chang_type(f2)],

["gcjs_zhaobiao_fangjian_old_gg",'http://www.lxggzyjy.com/f/trade/annogoods/list?tradeStatus=1&selectedProjectType=A',["name","ggstart_time","href","info"],add_info(f1,{"gclx":"房建市政"}),f2],
["gcjs_zhongbiao_fangjian_old_gg",'http://www.lxggzyjy.com/f/trade/annogoods/list?tradeStatus=1&selectedProjectType=A',["name","ggstart_time","href","info"],chang_type(add_info(f1,{"gclx":"房建市政"})),chang_type(f2)],

["gcjs_zhaobiao_shuili_gg",'http://www.lxggzyjy.com/f/newtrade/annogoods/list?selectedProjectType=4',["name","ggstart_time","href","info"],add_info(f1,{"gclx":"水利工程"}),f2],
["gcjs_zhongbiao_shuili_gg",'http://www.lxggzyjy.com/f/newtrade/annogoods/list?selectedProjectType=4',["name","ggstart_time","href","info"],chang_type(add_info(f1,{"gclx":"水利工程"})),chang_type(f2)],

["gcjs_zhaobiao_shuili_old_gg",'http://www.lxggzyjy.com/f/trade/annogoods/list?tradeStatus=1&selectedProjectType=A03',["name","ggstart_time","href","info"],add_info(f1,{"gclx":"水利工程"}),f2],
["gcjs_zhongbiao_shuili_old_gg",'http://www.lxggzyjy.com/f/trade/annogoods/list?tradeStatus=1&selectedProjectType=A03',["name","ggstart_time","href","info"],chang_type(add_info(f1,{"gclx":"水利工程"})),chang_type(f2)],

["gcjs_zhaobiao_zhonghe_gg",'http://www.lxggzyjy.com/f/newtrade/annogoods/list?selectedProjectType=5',["name","ggstart_time","href","info"],add_info(f1,{"gclx":"综合类项目"}),f2],
["gcjs_zhongbiao_zhonghe_gg",'http://www.lxggzyjy.com/f/newtrade/annogoods/list?selectedProjectType=5',["name","ggstart_time","href","info"],chang_type(add_info(f1,{"gclx":"综合类项目"})),chang_type(f2)],

["gcjs_zhaobiao_zhonghe_old_gg",'http://www.lxggzyjy.com/f/trade/annogoods/list?tradeStatus=1&selectedProjectType=C',["name","ggstart_time","href","info"],add_info(f1,{"gclx":"综合类项目"}),f2],
["gcjs_zhongbiao_zhonghe_old_gg",'http://www.lxggzyjy.com/f/trade/annogoods/list?tradeStatus=1&selectedProjectType=C',["name","ggstart_time","href","info"],chang_type(add_info(f1,{"gclx":"综合类项目"})),chang_type(f2)],

["zfcg_zhaobiao_gg",'http://www.lxggzyjy.com/f/newtrade/annogoods/list?selectedProjectType=2',["name","ggstart_time","href","info"],f1,f2],
["zfcg_zhongbiao_gg",'http://www.lxggzyjy.com/f/newtrade/annogoods/list?selectedProjectType=2',["name","ggstart_time","href","info"],chang_type(f1),chang_type(f2)],

["zfcg_zhaobiao_old_gg",'http://www.lxggzyjy.com/f/trade/annogoods/list?tradeStatus=1&selectedProjectType=D',["name","ggstart_time","href","info"],f1,f2],
["zfcg_zhongbiao_old_gg",'http://www.lxggzyjy.com/f/trade/annogoods/list?tradeStatus=1&selectedProjectType=D',["name","ggstart_time","href","info"],chang_type(f1),chang_type(f2)],

["zfcg_zhaobiao_xieyi_gg",'http://www.lxggzyjy.com/f/newtrade/annogoods/list?selectedProjectType=9',["name","ggstart_time","href","info"],add_info(f1,{"gclx":"协议供货"}),f2],
["zfcg_zhongbiao_xieyi_gg",'http://www.lxggzyjy.com/f/newtrade/annogoods/list?selectedProjectType=9',["name","ggstart_time","href","info"],chang_type(add_info(f1,{"gclx":"协议供货"})),chang_type(f2)],

["zfcg_zhaobiao_xiane_gg",'http://www.lxggzyjy.com/f/newtrade/annogoods/list?selectedProjectType=11',["name","ggstart_time","href","info"],add_info(f1,{"gclx":"限额以下"}),f2],
["zfcg_zhongbiao_xiane_gg",'http://www.lxggzyjy.com/f/newtrade/annogoods/list?selectedProjectType=11',["name","ggstart_time","href","info"],chang_type(add_info(f1,{"gclx":"限额以下"})),chang_type(f2)],

["gcjs_zhaobiao_xiane_gg",'http://www.lxggzyjy.com/f/newtrade/annogoods/list?selectedProjectType=10',["name","ggstart_time","href","info"],add_info(f1,{"gclx":"限额以下"}),f2],
["gcjs_zhongbiao_xiane_gg",'http://www.lxggzyjy.com/f/newtrade/annogoods/list?selectedProjectType=10',["name","ggstart_time","href","info"],chang_type(add_info(f1,{"gclx":"限额以下"})),chang_type(f2)],


    ]

def work(conp,**args):
    est_meta(conp,data=data,diqu="甘肃省临夏市",**args)
    est_html(conp,f=f3,**args)


if __name__=="__main__":
    work(conp=["postgres","since2015",'192.168.3.171',"lchest","ggzy_gansu_linxia"],headless=False,num=1,total=2)
    # driver=webdriver.Chrome()
    # f3(driver,'http://www.qyggfw.cn/w/bid/purchaseQualiInqueryAnn/37304/details.html')
