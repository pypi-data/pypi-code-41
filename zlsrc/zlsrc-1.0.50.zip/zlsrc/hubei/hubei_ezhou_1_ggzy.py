import pandas as pd
import re
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
import json
from zlsrc.util.etl import add_info,est_meta,est_html,est_tbs



def f1(driver, num):
    locator = (By.XPATH, "//pre[string-length()>100]")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    cnum = int(re.findall(r'page=(\d+)', url)[0])
    if num != cnum:
        pre1 = driver.find_element_by_xpath("//pre").text.strip()
        datas1 = json.loads(pre1)
        rows1 = datas1['rows'][0]
        val1 = rows1['gongShiGuid']
        s = 'page=%d' % num if num>1 else 'page=1'
        url = re.sub('page=[0-9]+', s, url)
        driver.get(url)
        locator = (By.XPATH, "//pre[string-length()>100]")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
        pre2 = driver.find_element_by_xpath("//pre").text.strip()
        datas2 = json.loads(pre2)
        rows2 = datas2['rows'][0]
        val2 = rows2['gongShiGuid']
        if val1 == val2:
            raise ValueError
    data = []
    pre = driver.find_element_by_xpath("//pre").text.strip()
    datas = json.loads(pre)
    rows = datas['rows']
    url = driver.current_url
    tp = re.findall(r'type=(\d+)', url)[0]
    gongShiType = re.findall(r'gongShiType=(\d+)', url)[0]
    for tr in rows:
        info = {}
        name = tr['title']
        ggstart_time = tr['faBuStartTimeText']
        # gcjs
        if tp == '10':
            if gongShiType == '10':
                href = 'http://ggzyj.ezhou.gov.cn/jiaoyixingxi/zbgg_view.html?guid=' + tr['yuanXiTongId']
            elif gongShiType == '170':
                href = 'http://ggzyj.ezhou.gov.cn/jiaoyixingxi/bggs_view.html?guid=' + tr['yuanXiTongId']
            elif gongShiType  == '180':
                href = 'http://ggzyj.ezhou.gov.cn/jiaoyixingxi/pbjg_view.html?guid=' + tr['yuanXiTongId']
            elif gongShiType == '50':
                href = 'http://ggzyj.ezhou.gov.cn/jiaoyixingxi/zbgs_view.html?guid=' + tr['yuanXiTongId']
            elif gongShiType == '130':
                href = 'http://ggzyj.ezhou.gov.cn/jiaoyixingxi/ycxx_view.html?guid=' + tr['yuanXiTongId']
            elif gongShiType == 'kzj':
                href = 'http://ggzyj.ezhou.gov.cn/jiaoyixingxi/kzjgs_view.html?guid=' + tr['yuanXiTongId']
            else:
                href = 'http://ggzyj.ezhou.gov.cn/jiaoyixingxi/zbsb_view.html?guid=' + tr['yuanXiTongId']
        # zfcg
        if tp == '20':
            if gongShiType == '70':
                cgptflag = tr['cgptflag']
                if cgptflag and (cgptflag != '0'):
                    if int(cgptflag) ==1:
                        href = 'http://www.ezggzy.cn/zcsc/wssc/caiGouXinXi/toJingJiaBulletenDetail.html?guid=' + tr['yuanXiTongId']
                    elif int(cgptflag) ==2:
                        href = 'http://www.ezggzy.cn/zcsc/wssc/caiGouXinXi/toZhiGouBulletenDetail.html?guid=' + tr['yuanXiTongId']
                else:
                    href = 'http://ggzyj.ezhou.gov.cn/jiaoyizfcg/zbgg_view.html?guid=' + tr['yuanXiTongId']
            elif gongShiType == '170':
                cgptflag = tr['cgptflag']
                if cgptflag and (cgptflag != '0'):
                    if int(cgptflag) == 5:
                        href = 'http://www.ezggzy.cn/zcsc/wssc/caiGouXinXi/toBuYiBulletenDetail.html?guid=' + tr['yuanXiTongId']
                else:
                    href = 'http://ggzyj.ezhou.gov.cn/jiaoyizfcg/bggs_view.html?guid=' + tr['yuanXiTongId']

            elif gongShiType == '50':
                cgptflag = tr['cgptflag']
                if cgptflag and (cgptflag != '0'):
                    if int(cgptflag) == 3:
                        href = 'http://www.ezggzy.cn/zcsc/wssc/caiGouXinXi/toJingJiaResultDetail.html?guid=' + tr['yuanXiTongId']
                    elif int(cgptflag) == 4:
                        href = 'http://www.ezggzy.cn/zcsc/wssc/caiGouXinXi/toZhiGouResultDetail.html?guid=' + tr['yuanXiTongId']
                else:
                    href = 'http://ggzyj.ezhou.gov.cn/jiaoyizfcg/zbgs_view.html?guid=' + tr['yuanXiTongId']

            elif gongShiType == '130':
                href = 'http://ggzyj.ezhou.gov.cn/jiaoyizfcg/ycxx_view.html?guid=' + tr['yuanXiTongId']

        bianhao = tr['bianHao']
        if bianhao:info['biaohao']=bianhao
        xmlx = tr['gongChengTypeText']
        if xmlx: info['xmlx'] = xmlx
        cglx = tr['gongChengLeiBieText']
        if cglx: info['cglx'] = cglx
        if info:
            info = json.dumps(info, ensure_ascii=False)
        else:info = None
        tmp = [name, ggstart_time, href, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    locator = (By.XPATH, "//pre[string-length()>100]")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    pre = driver.find_element_by_xpath("//pre").text.strip()
    datas = json.loads(pre)
    num = datas['totalPage']
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='xmmc_bt'][string-length()>40] | //div[@class='content_nr'][string-length()>40]")
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
    div = soup.find('div', class_='xmmc_bt')
    if div == None:
        div = soup.find('div', class_='content_nr')
    return div


data = [
    ["gcjs_zhaobiao_gg",
     "http://ggzyj.ezhou.gov.cn/jiaoyixinxi/queryJiaoYiXinXiPagination.do?bianHao=&gongChengLeiBie=&gongChengType=&gongShiType=10&page=1&rows=15&title=&type=10",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_biangeng_gg",
     "http://ggzyj.ezhou.gov.cn/jiaoyixinxi/queryJiaoYiXinXiPagination.do?bianHao=&gongChengLeiBie=&gongChengType=&gongShiType=170&page=1&rows=15&title=&type=10",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["gcjs_zhongbiaohx_gg",
     "http://ggzyj.ezhou.gov.cn/jiaoyixinxi/queryJiaoYiXinXiPagination.do?bianHao=&gongChengLeiBie=&gongChengType=&gongShiType=180&page=1&rows=15&title=&type=10",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongbiao_gg",
     "http://ggzyj.ezhou.gov.cn/jiaoyixinxi/queryJiaoYiXinXiPagination.do?bianHao=&gongChengLeiBie=&gongChengType=&gongShiType=50&page=1&rows=15&title=&type=10",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["gcjs_zhongzhi_gg",
     "http://ggzyj.ezhou.gov.cn/jiaoyixinxi/queryJiaoYiXinXiPagination.do?bianHao=&gongChengLeiBie=&gongChengType=&gongShiType=130&page=1&rows=15&title=&type=10",
     ["name", "ggstart_time", "href", "info"], f1, f2],
###
    ["zfcg_zhaobiao_gg",
     "http://ggzyj.ezhou.gov.cn/jiaoyixinxi/queryJiaoYiXinXiPagination.do?bianHao=&gongChengLeiBie=&gongChengType=&gongShiType=70&page=1&rows=15&title=&type=20",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_gqita_bian_cheng_gg",
     "http://ggzyj.ezhou.gov.cn/jiaoyixinxi/queryJiaoYiXinXiPagination.do?bianHao=&gongChengLeiBie=&gongChengType=&gongShiType=170&page=1&rows=15&title=&type=20",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhongbiao_gg",
     "http://ggzyj.ezhou.gov.cn/jiaoyixinxi/queryJiaoYiXinXiPagination.do?bianHao=&gongChengLeiBie=&gongChengType=&gongShiType=50&page=1&rows=15&title=&type=20",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongzhi_gg",
     "http://ggzyj.ezhou.gov.cn/jiaoyixinxi/queryJiaoYiXinXiPagination.do?bianHao=&gongChengLeiBie=&gongChengType=&gongShiType=130&page=1&rows=15&title=&type=20",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp,**args):
    est_meta(conp,data=data,diqu="湖北省鄂州市",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':
    work(conp=["postgres","since2015","192.168.3.171","zlsrc","ezhoushi"])

    # for d in data[5:]:
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

