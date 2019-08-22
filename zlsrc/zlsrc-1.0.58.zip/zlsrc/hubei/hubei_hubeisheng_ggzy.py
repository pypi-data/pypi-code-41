import pandas as pd
import re
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import sys
import time
import json
from zlsrc.util.etl import est_tbs, est_meta, est_html,  add_info




def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='wb-data-item']/li[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum=driver.find_element_by_xpath("//li[@class='active']/a").text
    url = driver.current_url
    if int(num) != int(cnum):
        val = driver.find_element_by_xpath("//ul[@class='wb-data-item']/li[last()]//a").get_attribute('href')[-30:]
        if 'about' in url:
            s = '/%d.html' % num if num >1 else '/about.html'
            url = re.sub('/about\.html', s, url)
        elif num == 1:
            url = re.sub('/[0-9]+\.html', '/about.html', url)
        else:
            s = '/%d.html' % num if num > 1 else '/about.html'
            url = re.sub('/[0-9]+\.html', s, url)
        driver.get(url)
        # 第二个等待
        locator = (By.XPATH, '//ul[@class="wb-data-item"]/li[last()]//a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('ul', class_='wb-data-item')
    lis = div.find_all('li')
    for tr in lis:
        href=tr.find('a')['href']
        name=tr.find('a')['title']
        ggstart_time=tr.find('span', class_='wb-data-date').get_text(strip=True)
        if 'http' in href:
            href = href
        else:
            href = 'http://www.hbbidcloud.cn' + href
        info = {}
        if re.findall(r'^【(.*?)】', name):
            laiyuan = re.findall(r'^【(.*?)】', name)[0]
            info['laiyuan']=laiyuan
        if info:info= json.dumps(info, ensure_ascii=False)
        else:info = None
        tmp = [name, ggstart_time, href, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df


def f2(driver):
    locator = (By.XPATH, "//ul[@class='wb-data-item']/li[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))

    num = driver.find_element_by_xpath("//ul[@class='m-pagination-page']/li[last()]/a").text.strip()
    driver.quit()
    return int(num)





def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@id='infoContentM'][string-length()>100]")
    WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
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
    div = soup.find('div', class_='news-article')
    if div == None:
        raise ValueError('div is None')
    return div


data = [
    ["gcjs_gqita_zhuce_fj_gg", "http://www.hbbidcloud.cn/hubei/jyxx/004001/004001001/about.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{"gglx":"项目注册", "gclx":"房建市政"}), f2],

    ["gcjs_gqita_zhuce_sl_gg", "http://www.hbbidcloud.cn/hubei/jyxx/004001/004001002/about.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"gglx": "项目注册", "gclx": "水利工程"}), f2],

    ["gcjs_gqita_zhuce_jt_gg", "http://www.hbbidcloud.cn/hubei/jyxx/004001/004001003/about.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"gglx": "项目注册", "gclx": "交通工程"}), f2],

    ["gcjs_gqita_zhuce_tl_gg", "http://www.hbbidcloud.cn/hubei/jyxx/004001/004001004/about.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"gglx": "项目注册", "gclx": "铁路工程"}), f2],

    ["gcjs_gqita_zhuce_td_gg", "http://www.hbbidcloud.cn/hubei/jyxx/004001/004001005/about.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"gglx": "项目注册", "gclx": "土地整治"}), f2],

    ["gcjs_gqita_zhuce_qt_gg", "http://www.hbbidcloud.cn/hubei/jyxx/004001/004001006/about.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"gglx": "项目注册", "gclx": "其他工程"}), f2],

    ####
    ["gcjs_zhaobiao_fj_gg", "http://www.hbbidcloud.cn/hubei/jyxx/004002/004002001/about.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"gclx": "房建市政"}), f2],

    ["gcjs_zhaobiao_sl_gg", "http://www.hbbidcloud.cn/hubei/jyxx/004002/004002002/about.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"gclx": "水利工程"}), f2],

    ["gcjs_zhaobiao_jt_gg", "http://www.hbbidcloud.cn/hubei/jyxx/004002/004002003/about.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"gclx": "交通工程"}), f2],

    ["gcjs_zhaobiao_tl_gg", "http://www.hbbidcloud.cn/hubei/jyxx/004002/004002004/about.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"gclx": "铁路工程"}), f2],

    ["gcjs_zhaobiao_td_gg", "http://www.hbbidcloud.cn/hubei/jyxx/004002/004002005/about.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"gclx": "土地整治"}), f2],

    ["gcjs_zhaobiao_qt_gg", "http://www.hbbidcloud.cn/hubei/jyxx/004002/004002006/about.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"gclx": "其他工程"}), f2],

    ####
    ["gcjs_gqita_liu_cheng_fj_gg", "http://www.hbbidcloud.cn/hubei/jyxx/004003/004003001/about.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"gclx": "房建市政"}), f2],

    ["gcjs_gqita_liu_cheng_sl_gg", "http://www.hbbidcloud.cn/hubei/jyxx/004003/004003002/about.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"gclx": "水利工程"}), f2],

    ["gcjs_gqita_liu_cheng_jt_gg", "http://www.hbbidcloud.cn/hubei/jyxx/004003/004003003/about.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"gclx": "交通工程"}), f2],

    ["gcjs_gqita_liu_cheng_tl_gg", "http://www.hbbidcloud.cn/hubei/jyxx/004003/004003004/about.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"gclx": "铁路工程"}), f2],

    ["gcjs_gqita_liu_cheng_td_gg", "http://www.hbbidcloud.cn/hubei/jyxx/004003/004003005/about.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"gclx": "土地整治"}), f2],

    ["gcjs_gqita_liu_cheng_qt_gg", "http://www.hbbidcloud.cn/hubei/jyxx/004003/004003006/about.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"gclx": "其他工程"}), f2],

    ####
    ["gcjs_zhongbiaohx_fj_gg", "http://www.hbbidcloud.cn/hubei/jyxx/004004/004004001/about.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"gclx": "房建市政"}), f2],

    ["gcjs_zhongbiaohx_sl_gg", "http://www.hbbidcloud.cn/hubei/jyxx/004004/004004002/about.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"gclx": "水利工程"}), f2],

    ["gcjs_zhongbiaohx_jt_gg", "http://www.hbbidcloud.cn/hubei/jyxx/004004/004004003/about.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"gclx": "交通工程"}), f2],

    ["gcjs_zhongbiaohx_tl_gg", "http://www.hbbidcloud.cn/hubei/jyxx/004004/004004004/about.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"gclx": "铁路工程"}), f2],

    ["gcjs_zhongbiaohx_td_gg", "http://www.hbbidcloud.cn/hubei/jyxx/004004/004004005/about.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"gclx": "土地整治"}), f2],

    ["gcjs_zhongbiaohx_qt_gg", "http://www.hbbidcloud.cn/hubei/jyxx/004004/004004006/about.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"gclx": "其他工程"}), f2],

    ####
    ["gcjs_zhongbiao_fj_gg", "http://www.hbbidcloud.cn/hubei/jyxx/004005/004005001/about.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"gclx": "房建市政"}), f2],

    ["gcjs_zhongbiao_sl_gg", "http://www.hbbidcloud.cn/hubei/jyxx/004005/004005002/about.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"gclx": "水利工程"}), f2],

    ["gcjs_zhongbiao_jt_gg", "http://www.hbbidcloud.cn/hubei/jyxx/004005/004005003/about.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"gclx": "交通工程"}), f2],

    ["gcjs_zhongbiao_tl_gg", "http://www.hbbidcloud.cn/hubei/jyxx/004005/004005004/about.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"gclx": "铁路工程"}), f2],

    ["gcjs_zhongbiao_td_gg", "http://www.hbbidcloud.cn/hubei/jyxx/004005/004005005/about.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"gclx": "土地整治"}), f2],

    ["gcjs_zhongbiao_qt_gg", "http://www.hbbidcloud.cn/hubei/jyxx/004005/004005006/about.html",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {"gclx": "其他工程"}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="湖北省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlsrc", "ggzy_hubei_hubei2"], total=2, headless=True, num=1)

    # for d in data:
    #     driver=webdriver.Chrome()
    #     url=d[1]
    #     print(url)
    #     driver.get(url)
    #     df = f2(driver)
    #     print(df)
    #     driver = webdriver.Chrome()
    #     driver.get(url)
    #
    #     df=f1(driver, 4)
    #     print(df.values)
    #     for f in df[2].values:
    #         print(f)
    #         d = f3(driver, f)
    #         print(d)

