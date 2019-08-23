import pandas as pd  
import re 
import json
from selenium import webdriver 
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 


import time

from zlsrc.util.etl import est_html,est_meta

def f1(driver,num):
    locator=(By.CLASS_NAME,"dataDiv")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    locator=(By.ID,"currentPage")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    cnum=int(driver.find_element_by_id("currentPage").text)
    if num!=cnum:
        val=driver.find_element_by_xpath("//div[@class='dataDiv']//tbody/tr[1]/td/span").text
        input1=driver.find_element_by_id("page_input")
        input1.clear()
        input1.send_keys(num)
        driver.execute_script("page.skip();")
        locator=(By.XPATH,"//div[@class='dataDiv']//tbody/tr[1]/td/span[string()!='%s']"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))


    page=driver.page_source 

    soup=BeautifulSoup(page,"html.parser")

    div=soup.find("div",class_="dataDiv")
    tbody=div.find("tbody")

    trs=tbody.find_all("tr")
    data=[]
    i=0
    for tr in trs:
        a=tr.find_all("td")[0]
        td=tr.find_all("td")[1]
        href=driver.execute_script("""
        var obj = dataList[%d];
        var sidebarIndex = parent.sidebarIndex || 1;
        var url = 'http://zyjy.huizhou.gov.cn/PublicServer/public/commonAnnouncement/showDetail.html?businessType='+businessType+'&sidebarIndex='+sidebarIndex+'&id='+obj.id;
        return url;
            """%i)
        
        i+=1
        diqus=re.findall('^【(.{,8})】',a.text)
        if diqus!=[]:
            diqu=diqus[0]
        else:
            diqu=''
        info=json.dumps({"diqu":diqu},ensure_ascii=False)
        tmp=[a["title"],td.text.strip(),href,info]
        data.append(tmp)
    df=pd.DataFrame(data=data)

    return df 

def f2(driver):

    locator=(By.CLASS_NAME,"dataDiv")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    locator=(By.ID,"totalPage")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    total=int(driver.find_element_by_id("totalPage").text)
    driver.quit()

    return total

def f3(driver,url):


    driver.get(url)

    WebDriverWait(driver, 10).until(lambda driver: len(driver.current_url) > 10)

    try:
        time.sleep(0.5)
        mark=driver.find_element_by_xpath('//div[@class="layui-layer-content"]').text
        if '撤回' in mark:
            return '该公告已撤回'
    except:
        pass

    locator=(By.XPATH,'//div[@id="content"][string-length()>50]')

    WebDriverWait(driver,10).until(EC.presence_of_all_elements_located(locator))



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

    div=soup.find('div',id='body')

    
    return div

data=[
        ["gcjs_zhaobiao_gg","http://zyjy.huizhou.gov.cn/PublicServer/public/commonAnnouncement/listPage.html?businessType=2&announcementType=20",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_biangeng_gg","http://zyjy.huizhou.gov.cn/PublicServer/public/commonAnnouncement/listPage.html?businessType=2&announcementType=23",["name","ggstart_time","href","info"],f1,f2],

        ["gcjs_zhongbiaohx_gg","http://zyjy.huizhou.gov.cn/PublicServer/public/commonAnnouncement/listPage.html?businessType=2&announcementType=22",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_zhaobiao_gg","http://zyjy.huizhou.gov.cn/PublicServer/public/commonAnnouncement/listPage.html?businessType=1&announcementType=10",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_biangeng_gg","http://zyjy.huizhou.gov.cn/PublicServer/public/commonAnnouncement/listPage.html?businessType=1&announcementType=11",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_zhongbiao_gg","http://zyjy.huizhou.gov.cn/PublicServer/public/commonAnnouncement/listPage.html?businessType=1&announcementType=12",["name","ggstart_time","href","info"],f1,f2],

        ["zfcg_liubiao_gg","http://zyjy.huizhou.gov.cn/PublicServer/public/commonAnnouncement/listPage.html?businessType=1&announcementType=19",["name","ggstart_time","href","info"],f1,f2],
    ]



def work(conp,**args):
    est_meta(conp,data=data,diqu="广东省惠州市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    # work(conp=["postgres","since2015","127.0.0.1","guangdong","huizhou"])
    driver=webdriver.Chrome()
    f=f3(driver,'http://zyjy.huizhou.gov.cn/PublicServer/public/commonAnnouncement/showDetail.html?businessType=2&sidebarIndex=1&id=a0e0dd440c864f7d932129c4f63d0e40')
    print(f)