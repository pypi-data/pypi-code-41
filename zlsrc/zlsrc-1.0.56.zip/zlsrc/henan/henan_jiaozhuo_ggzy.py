import pandas as pd  
import re
from selenium import webdriver 
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
import time
from zlsrc.util.etl import est_meta,est_html




def f1(driver,num):
    locator=(By.XPATH,"//table[@id='MoreInfoList1_DataGrid1']//tr//a")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    #url=driver.current_url
    cnum=int(driver.find_element_by_xpath("//div[@id='MoreInfoList1_Pager']//font[@color='red']").text.strip())
    if num!=cnum:
        
        val=driver.find_element_by_xpath("//table[@id='MoreInfoList1_DataGrid1']//tr[last()]//a").get_attribute('href')[-45:]
        driver.execute_script("javascript:__doPostBack('MoreInfoList1$Pager','%s')"%str(num))

        locator=(By.XPATH,"//table[@id='MoreInfoList1_DataGrid1']//tr[last()]//a[not(contains(@href,'%s'))]"%val)
        WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))

    page=driver.page_source
    soup=BeautifulSoup(page,"html.parser")
    div=soup.find("table",id="MoreInfoList1_DataGrid1")
    trs=div.find_all("tr")
    data=[]
    for tr in trs:
        a=tr.find("a")
        ggstart_time=tr.find_all("td")[-1].text.strip()
        tmp=[a["title"].strip(),ggstart_time,"http://www.jzggzy.cn"+a["href"]]
        data.append(tmp)
    df=pd.DataFrame(data=data)
    df["info"]=None
    return df 


def f2(driver):
    locator=(By.ID,"MoreInfoList1_Pager")
    WebDriverWait(driver,10).until(EC.presence_of_element_located(locator))
    total=driver.find_element_by_xpath("//div[@id='MoreInfoList1_Pager']/div[1]").text.strip()
    total=re.findall("总页数：([0-9]{1,})",total)[0]
    total=int(total)
    driver.quit()
    return total



def f3(driver,url):
    driver.get(url)
    try:
        locator=(By.XPATH,"//div[contains(@id,'menutab') and @style=''][string-length()>100] | //div[contains(@id,'menutab') and not(@style)][string-length()>100]")
        WebDriverWait(driver,10).until(EC.presence_of_all_elements_located(locator))
        flag = 1
    except:
        locator=(By.XPATH,"//table[@id='tblInfo'][string-length()>100]")
        WebDriverWait(driver,10).until(EC.presence_of_all_elements_located(locator))
        flag = 2
    before=len(driver.page_source)
    time.sleep(0.5)
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
    if flag == 1:
        div = soup.find("div", id=re.compile("menutab.*"), style="")
    elif flag == 2:
        div = soup.find('table', id='tblInfo')
    else:
        raise ValueError
    return div

data=[
    ["gcjs_zhaobiao_gg","http://www.jzggzy.cn/TPFront/ztbzx/069002/069002001/069002001001/MoreInfo.aspx?CategoryNum=69002001001",["name","ggstart_time","href","info"],f1,f2],

    ["gcjs_biangeng_gg","http://www.jzggzy.cn/TPFront/ztbzx/069002/069002001/069002001002/MoreInfo.aspx?CategoryNum=69002001002",["name","ggstart_time","href","info"],f1,f2],

    ["gcjs_kongzhijia_gg","http://www.jzggzy.cn/TPFront/ztbzx/069002/069002001/069002001003/MoreInfo.aspx?CategoryNum=69002001003",["name","ggstart_time","href","info"],f1,f2],

    ["gcjs_yucai_gg","http://www.jzggzy.cn/TPFront/ztbzx/069002/069002001/069002001004/MoreInfo.aspx?CategoryNum=69002001004",["name","ggstart_time","href","info"],f1,f2],


    ["gcjs_zhongbiaohx_gg","http://www.jzggzy.cn/TPFront/ztbzx/069002/069002001/069002001005/MoreInfo.aspx?CategoryNum=69002001005",["name","ggstart_time","href","info"],f1,f2],

    ["zfcg_yucai_gg","http://www.jzggzy.cn/TPFront/ztbzx/069002/069002002/069002002003/MoreInfo.aspx?CategoryNum=69002002003",["name","ggstart_time","href","info"],f1,f2],

    ["zfcg_zhaobiao_gg","http://www.jzggzy.cn/TPFront/ztbzx/069002/069002002/069002002001/MoreInfo.aspx?CategoryNum=69002002001",["name","ggstart_time","href","info"],f1,f2],

    ["zfcg_biangeng_gg","http://www.jzggzy.cn/TPFront/ztbzx/069002/069002002/069002002002/MoreInfo.aspx?CategoryNum=69002002002",["name","ggstart_time","href","info"],f1,f2],


    ["zfcg_zhongbiaohx_gg","http://www.jzggzy.cn/TPFront/ztbzx/069002/069002002/069002002004/MoreInfo.aspx?CategoryNum=69002002004",["name","ggstart_time","href","info"],f1,f2],

    ["yiliao_zhaobiao_gg","http://www.jzggzy.cn/TPFront/ztbzx/069002/069002005/069002005001/MoreInfo.aspx?CategoryNum=69002005001",["name","ggstart_time","href","info"],f1,f2],

    ["yiliao_biangeng_gg","http://www.jzggzy.cn/TPFront/ztbzx/069002/069002005/069002005002/MoreInfo.aspx?CategoryNum=69002005002",["name","ggstart_time","href","info"],f1,f2],

    #["yiliao_yucai_gg","http://www.jzggzy.cn/TPFront/ztbzx/069002/069002005/069002005003/MoreInfo.aspx?CategoryNum=69002005003",["name","ggstart_time","href","info"],f1,f2],

    ["yiliao_zhongbiaohx_gg","http://www.jzggzy.cn/TPFront/ztbzx/069002/069002005/069002005004/MoreInfo.aspx?CategoryNum=69002005004",["name","ggstart_time","href","info"],f1,f2],
    ]


def work(conp,**args):
    est_meta(conp,data=data,diqu="河南省焦作市",**args)
    est_html(conp,f=f3,**args)

# 修改日期：2019/7/8
if __name__=="__main__":
    work(conp=["postgres","since2015","127.0.0.1","henan","jiaozhuo"])


    # for d in data[-2:]:
    #     driver=webdriver.Chrome()
    #     url=d[1]
    #     print(url)
    #     driver.get(url)
    #     df = f2(driver)
    #     print(df)
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #
    #     df=f1(driver, 1)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)
    # driver = webdriver.Chrome()
    # df = f3(driver, 'http://www.jzggzy.cn/TPFront/ZtbDetail/ZtbZfDetail.aspx?type=3&InfoID=9c895e88-5d82-44b2-9082-1dbdd6abe672&CategoryNum=069002002004')
    # print(df)