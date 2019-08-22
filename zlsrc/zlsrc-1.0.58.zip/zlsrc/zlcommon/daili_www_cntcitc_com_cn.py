import random
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from zlsrc.util.fake_useragent import UserAgent
from zlsrc.util.etl import est_html, est_meta, add_info, est_meta_large


def f1(driver, num):
    locator = (By.XPATH, "//div[@class='sid_txtli']/ul/li[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    locator = (By.XPATH, "//a[@class='sy_on']")
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()

    if num != int(cnum):
        val = driver.find_element_by_xpath("//div[@class='sid_txtli']/ul/li[last()]//a").get_attribute('onclick')
        val = re.findall(r"showArticle\('(.*)'\)", val)[0]

        driver.execute_script("go({},12)".format(num))
        # time.sleep(1)
        locator = (By.XPATH, "//div[@class='sid_txtli']/ul/li[last()]//a[not(contains(@onclick,'%s'))]" % val)
        WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', class_='sid_txtli').ul
    lis = div.find_all('li', recursive=False)
    for tr in lis:
        a = tr.find('a')
        try:
            name = a['title']
        except:
            name = a.text.strip()
        ggstart_time = tr.find('li', class_='sid_r').text.strip()
        ggstart_time = re.findall(r'(\d+-\d+-\d+)', ggstart_time)[0]
        href = a['onclick']
        tmp = [name, ggstart_time, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info']=None
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@class='sid_txtli']/ul/li[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//span[@class='shop_fenye']")
    total_page = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text.strip()
    num = re.findall(r'共(\d+)页', total_page)[0]
    driver.quit()
    return int(num)



def f3(driver, url):
    # driver.get(url)
    gContentId = re.findall(r"showArticle\('(.*)'\)", url)[0]
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
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'User-Agent': user_agent,
    }
    payloadData = {
        'gContentId': gContentId
    }
    # 下载超时
    timeOut = 60
    tt_url = 'http://www.cntcitc.com.cn/more/article.html'
    if proxies:
        res = requests.post(url=tt_url, headers=headers, data=payloadData, timeout=timeOut, proxies=proxies)
    else:
        res = requests.post(url=tt_url, headers=headers, data=payloadData, timeout=timeOut)
    # 需要判断是否为登录后的页面
    if res.status_code != 200:
        raise ConnectionError
    else:
        page = res.text
        soup = BeautifulSoup(page, 'html.parser')
        div = soup.find('div', class_='WordSection1')
        if div != None:
            div = soup.find('div', class_='sidebar_TAB')
        if div==None:raise ValueError
        return div


data = [

    ["jqita_zhaobiao_gg",
     "http://www.cntcitc.com.cn/more.html?chanType=3&chanId=12",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["jqita_gqita_gg",
     "http://www.cntcitc.com.cn/more.html?chanType=3&chanId=14",
     ["name", "ggstart_time", "href", "info"], f1 ,f2],

    ["jqita_zhongbiaohx_gg",
     "http://www.cntcitc.com.cn/more.html?chanType=3&chanId=16",
     ["name", "ggstart_time", "href", "info"],f1 ,f2],

    ["jqita_zhongbiao_gg",
     "http://www.cntcitc.com.cn/more.html?chanType=3&chanId=13",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


##中招国际招标有限公司
def work(conp, **args):
    est_meta(conp, data=data, diqu="中招国际招标有限公司", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "www_cntcitc_com_cn"])


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
    #     df=f1(driver, 12)
    #     print(df.values)
        # for f in df[2].values:
        #     d = f3(driver, f)
        #     print(d)


