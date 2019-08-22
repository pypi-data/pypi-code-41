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




def f1(driver, num):
    locator = (By.XPATH, "//div[@id='list_right']/ul/li[last()]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    locator = (By.XPATH, "//p[@class='yeshu']")
    total_page = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    cnum = re.findall(r'(\d+)页', total_page)[1]
    # print(cnum)

    if num != int(cnum):
        val = driver.find_element_by_xpath("//div[@id='list_right']/ul/li[last()]/a").get_attribute('href')[-20:]

        driver.execute_script("changePage({})".format(num))
        locator = (By.XPATH, "//div[@id='list_right']/ul/li[last()]/a[not(contains(@href,'%s'))]" % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    time.sleep(1)
    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find('div', id='list_right').ul
    lis = table.find_all('li')
    for tr in lis:
        a = tr.find('a')
        try:
            name = a['title']
        except:
            name = a.text.strip()
        ggstart_time = tr.find_all('span')[-1].text.strip()
        href = 'http://www.ccgp-jilin.gov.cn'+a['href']
        if 'categoryId=125' in url:
            diqu = tr.find('em').text.strip()
            info = json.dumps({'diqu':diqu}, ensure_ascii=False)
        else:info = None
        tmp = [name, ggstart_time, href, info]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    return df



def f2(driver):
    locator = (By.XPATH, "//div[@id='list_right']/ul/li[last()]/a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    locator = (By.XPATH, "//p[@class='yeshu']")
    total_page = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    num = int(re.findall(r'(\d+)页', total_page)[0])
    driver.quit()
    return num



def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[contains(@id, 'xiangqingneiron')]/span[string-length()>70]")
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
    div = soup.find('div', id='xiangqingneiron')
    return div


data = [
    ["zfcg_zgys_shengji_gg",
     "http://www.ccgp-jilin.gov.cn/shopHome/morePolicyNews.action?categoryId=124&noticetypeId=1",
     ["name", "ggstart_time", "href", "info"],f1,f2],

    ["zfcg_zhaobiao_gk_shengji_gg",
     "http://www.ccgp-jilin.gov.cn/shopHome/morePolicyNews.action?categoryId=124&noticetypeId=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'zbfs':'公开招标'}), f2],

    ["zfcg_zhaobiao_yq_shengji_gg",
     "http://www.ccgp-jilin.gov.cn/shopHome/morePolicyNews.action?categoryId=124&noticetypeId=7",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '邀请招标'}), f2],

    ["zfcg_zhaobiao_tp_shengji_gg",
     "http://www.ccgp-jilin.gov.cn/shopHome/morePolicyNews.action?categoryId=124&noticetypeId=4",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '竞争性谈判'}), f2],

    ["zfcg_zhaobiao_cs_shengji_gg",
     "http://www.ccgp-jilin.gov.cn/shopHome/morePolicyNews.action?categoryId=124&noticetypeId=5",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '竞争性磋商'}), f2],

    ["zfcg_dyly_shengji_gg",
     "http://www.ccgp-jilin.gov.cn/shopHome/morePolicyNews.action?categoryId=124&noticetypeId=6",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_xj_shengji_gg",
     "http://www.ccgp-jilin.gov.cn/shopHome/morePolicyNews.action?categoryId=124&noticetypeId=3",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '询价招标'}), f2],

    ["zfcg_zhongbiao_shengji_gg",
     "http://www.ccgp-jilin.gov.cn/shopHome/morePolicyNews.action?categoryId=124&noticetypeId=9",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_zhong_he_shengji_gg",
     "http://www.ccgp-jilin.gov.cn/shopHome/morePolicyNews.action?categoryId=124&noticetypeId=10",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_liu_bian_shengji_gg",
     "http://www.ccgp-jilin.gov.cn/shopHome/morePolicyNews.action?categoryId=124&noticetypeId=11,12,8",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_he_yan_shengji_gg",
     "http://www.ccgp-jilin.gov.cn/shopHome/morePolicyNews.action?categoryId=124&noticetypeId=13,14",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ####
    ["zfcg_zgys_shixian_gg",
     "http://www.ccgp-jilin.gov.cn/shopHome/morePolicyNews.action?categoryId=125&noticetypeId=1",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_gk_shixian_gg",
     "http://www.ccgp-jilin.gov.cn/shopHome/morePolicyNews.action?categoryId=125&noticetypeId=2",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '公开招标'}), f2],

    ["zfcg_zhaobiao_yq_shixian_gg",
     "http://www.ccgp-jilin.gov.cn/shopHome/morePolicyNews.action?categoryId=125&noticetypeId=7",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '邀请招标'}), f2],

    ["zfcg_zhaobiao_tp_shixian_gg",
     "http://www.ccgp-jilin.gov.cn/shopHome/morePolicyNews.action?categoryId=125&noticetypeId=4",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '竞争性谈判'}), f2],

    ["zfcg_zhaobiao_cs_shixian_gg",
     "http://www.ccgp-jilin.gov.cn/shopHome/morePolicyNews.action?categoryId=125&noticetypeId=5",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '竞争性磋商'}), f2],

    ["zfcg_dyly_shixian_gg",
     "http://www.ccgp-jilin.gov.cn/shopHome/morePolicyNews.action?categoryId=125&noticetypeId=6",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhaobiao_xj_shixian_gg",
     "http://www.ccgp-jilin.gov.cn/shopHome/morePolicyNews.action?categoryId=125&noticetypeId=3",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'zbfs': '询价招标'}), f2],

    ["zfcg_zhongbiao_shixian_gg",
     "http://www.ccgp-jilin.gov.cn/shopHome/morePolicyNews.action?categoryId=125&noticetypeId=9",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_zhong_he_shixian_gg",
     "http://www.ccgp-jilin.gov.cn/shopHome/morePolicyNews.action?categoryId=125&noticetypeId=10",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_liu_bian_shixian_gg",
     "http://www.ccgp-jilin.gov.cn/shopHome/morePolicyNews.action?categoryId=125&noticetypeId=11,12,8",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_gqita_he_yan_shixian_gg",
     "http://www.ccgp-jilin.gov.cn/shopHome/morePolicyNews.action?categoryId=125&noticetypeId=13,14",
     ["name", "ggstart_time", "href", "info"], f1, f2],


]


def work(conp, **args):
    est_meta(conp, data=data, diqu="吉林省", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlsrc", "zfcg_jilin_jilin"])


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
    #     df=f1(driver, 2)
    #     print(df.values)
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)


