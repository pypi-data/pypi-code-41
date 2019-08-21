import pandas as pd  
import re 

from selenium import webdriver 
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 


import json

import time

from zlsrc.util.etl import est_html, est_meta, add_info


def f1(driver,num):
    locator=(By.XPATH,"//div[@class='nav_list']//li[1]//a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    url=driver.current_url

    cnum=re.findall("jsp\?page=([0-9]{1,})",url)[0]
    if num!=cnum:
        val=driver.find_element_by_xpath("//div[@class='nav_list']//li[1]//a").get_attribute('href')[-20:]

        url=re.sub("(?<=page=)[0-9]{1,}",str(num),url)
        locator=(By.XPATH,"//div[@class='nav_list']//li[1]//a[contains(@href,'%s')]"%val)
        driver.get(url)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    page=driver.page_source 
    soup=BeautifulSoup(page,"html.parser")

    div=soup.find("div",class_='nav_list')
    lis=div.find_all("li",class_="clear")

    data=[]
    for li in lis:
        a=li.find("a")
        span=li.find("span")
        href = a.get('href')
        if not href:
            continue
        href = href if 'http' in href else "http://ggzyjy.zs.gov.cn"+href

        name=a.get('title')
        ggstart_time=span.get_text(strip=True) if span.get_text(strip=True) else '-'

        tmp=[name,ggstart_time,href]
        # print(tmp)

        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df 

def f2(driver):
    locator=(By.XPATH,"//div[@class='nav_list']//li[1]//a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    locator=(By.XPATH,"//div[@class='f-page']//li[@class='pageintro']")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    li=driver.find_element_by_xpath("//div[@class='f-page']//li[@class='pageintro']").text
    total=re.findall("共([0-9]{1,})页",li)[0]
    total=int(total)
    driver.quit()
    return total


def f3(driver,url):

    driver.get(url)
    locator=(By.XPATH,'//iframe[@id="external-frame"]')

    WebDriverWait(driver,10).until(EC.presence_of_all_elements_located(locator))

    driver.switch_to.frame(0)
    locator = (By.XPATH, '//div[@class="articalDiv"][string-length()>100]')

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    before=len(driver.page_source)
    time.sleep(0.1)
    after=len(driver.page_source)
    i=0
    while before!=after:
        before=len(driver.page_source)
        time.sleep(0.1)
        after=len(driver.page_source)
        i+=1
        if i>5:break

    page=driver.page_source

    soup=BeautifulSoup(page,'html.parser')

    div=soup.find('div',class_=re.compile("details_\d"))

    driver.switch_to.default_content()

    return div


data=[
["gcjs_zhaobiao_gg","http://ggzyjy.zs.gov.cn/Application/NewPage/PageSubItem.jsp?page=1&node=58",["name","ggstart_time","href","info"],f1,f2],
["gcjs_gqita_da_bian_gg","http://ggzyjy.zs.gov.cn/Application/NewPage/PageSubItem.jsp?page=1&node=59",["name","ggstart_time","href","info"],f1,f2],
["gcjs_zhongbiaohx_gg","http://ggzyjy.zs.gov.cn/Application/NewPage/PageSubItem.jsp?page=1&node=60",["name","ggstart_time","href","info"],f1,f2],
["gcjs_zhongbiao_gg","http://ggzyjy.zs.gov.cn/Application/NewPage/PageSubItem.jsp?page=1&node=61",["name","ggstart_time","href","info"],f1,f2],
["gcjs_gqita_xiangmu_gg","http://ggzyjy.zs.gov.cn/Application/NewPage/PageSubItem.jsp?page=1&node=107",["name","ggstart_time","href","info"],add_info(f1,{"gclx":"项目公告"}),f2],
["gcjs_gqita_xinxi_gg","http://ggzyjy.zs.gov.cn/Application/NewPage/PageSubItem.jsp?page=1&node=172",["name","ggstart_time","href","info"],add_info(f1,{"gclx":"信息公开"}),f2],

["zfcg_zhaobiao_gg","http://ggzyjy.zs.gov.cn/Application/NewPage/PageSubItem.jsp?page=1&node=4",["name","ggstart_time","href","info"],f1,f2],
["zfcg_zhongbiao_gg","http://ggzyjy.zs.gov.cn/Application/NewPage/PageSubItem.jsp?page=1&node=55",["name","ggstart_time","href","info"],f1,f2],
["zfcg_biangeng_gg","http://ggzyjy.zs.gov.cn/Application/NewPage/PageSubItem.jsp?page=1&node=54",["name","ggstart_time","href","info"],f1,f2],
["zfcg_liubiao_gg","http://ggzyjy.zs.gov.cn/Application/NewPage/PageSubItem.jsp?page=1&node=138",["name","ggstart_time","href","info"],f1,f2],
["zfcg_yucai_gg","http://ggzyjy.zs.gov.cn/Application/NewPage/PageSubItem.jsp?page=1&node=160",["name","ggstart_time","href","info"],f1,f2],

["yiliao_zhaobiao_gg","http://ggzyjy.zs.gov.cn/Application/NewPage/PageSubItem.jsp?page=1&node=70",["name","ggstart_time","href","info"],f1,f2],
["yiliao_gqita_bian_da_gg","http://ggzyjy.zs.gov.cn/Application/NewPage/PageSubItem.jsp?page=1&node=93",["name","ggstart_time","href","info"],f1,f2],
["yiliao_zhongbiaohx_gg","http://ggzyjy.zs.gov.cn/Application/NewPage/PageSubItem.jsp?page=1&node=104",["name","ggstart_time","href","info"],f1,f2],
["yiliao_zhongbiao_gg","http://ggzyjy.zs.gov.cn/Application/NewPage/PageSubItem.jsp?page=1&node=105",["name","ggstart_time","href","info"],f1,f2],
["yiliao_liubiao_gg","http://ggzyjy.zs.gov.cn/Application/NewPage/PageSubItem.jsp?page=1&node=152",["name","ggstart_time","href","info"],f1,f2],

["qsy_zhaobiao_gg","http://ggzyjy.zs.gov.cn/Application/NewPage/PageSubItem.jsp?page=1&node=7",["name","ggstart_time","href","info"],f1,f2],
["qsy_gqita_da_bian_gg","http://ggzyjy.zs.gov.cn/Application/NewPage/PageSubItem.jsp?page=1&node=112",["name","ggstart_time","href","info"],f1,f2],
["qsy_zhongbiaohx_gg","http://ggzyjy.zs.gov.cn/Application/NewPage/PageSubItem.jsp?page=1&node=113",["name","ggstart_time","href","info"],f1,f2],
["qsy_zhongbiao_gg","http://ggzyjy.zs.gov.cn/Application/NewPage/PageSubItem.jsp?page=1&node=115",["name","ggstart_time","href","info"],f1,f2],
["qsy_liubiao_gg","http://ggzyjy.zs.gov.cn/Application/NewPage/PageSubItem.jsp?page=1&node=118",["name","ggstart_time","href","info"],f1,f2],
["qsy_gqita_yanqi_gg","http://ggzyjy.zs.gov.cn/Application/NewPage/PageSubItem.jsp?page=1&node=135",["name","ggstart_time","href","info"],add_info(f1,{"tag":"延期公告"}),f2],

["jqita_zhaobiao_paimai_gg","http://ggzyjy.zs.gov.cn/Application/NewPage/PageSubItem.jsp?page=1&node=116",["name","ggstart_time","href","info"],add_info(f1,{"zbfs":"拍卖"}),f2],
["jqita_zhongbiao_paimai_gg","http://ggzyjy.zs.gov.cn/Application/NewPage/PageSubItem.jsp?page=1&node=117",["name","ggstart_time","href","info"],add_info(f1,{"zbfs":"拍卖"}),f2],

]


##中山市公共资源交易中心
def work(conp,**args):
    est_meta(conp,data=data,diqu="广东省中山市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    # work(conp=["postgres","since2015","192.168.3.171","guangdong","zhongshan"],ipNum=0,num=1,headless=False)
    driver=webdriver.Chrome()
    f=f3(driver,"http://ggzyjy.zs.gov.cn/Application/NewPage/PageArtical_1.jsp?nodeID=152&articalID=99044")
    print(f)