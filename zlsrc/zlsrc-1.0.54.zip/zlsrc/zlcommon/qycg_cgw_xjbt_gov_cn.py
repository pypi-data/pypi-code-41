import pandas as pd
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from zlsrc.util.etl import est_html, est_meta, add_info, est_meta_large



def f1(driver, num):
    locator = (By.XPATH, "//ul[@class='ewb-info-items']/li[last()]//a | //div[@class='con']/ul/li[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url = driver.current_url
    try:
        locator = (By.XPATH, "//a[@class='current']")
        cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    except:
        cnum = 1

    if num != int(cnum):
        val = driver.find_element_by_xpath("//ul[@class='ewb-info-items']/li[last()]//a | //div[@class='con']/ul/li[last()]//a").get_attribute('href')[-20:]
        driver.find_element_by_xpath("//input[@class='z_num']").clear()
        driver.find_element_by_xpath("//input[@class='z_num']").send_keys(num)
        driver.find_element_by_xpath("//a[@class='z_pret']").click()
        try:
            locator = (By.XPATH, "//ul[@class='ewb-info-items']/li[last()]//a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))
        except:
            locator = (By.XPATH, "//div[@class='con']/ul/li[last()]//a[not(contains(@href, '%s'))]" % val)
            WebDriverWait(driver, 20).until(EC.presence_of_element_located(locator))

    page = driver.page_source
    soup = BeautifulSoup(page, "html.parser")
    div = soup.find("ul", class_='ewb-info-items')
    if div == None:
        d = soup.find("div", class_='con').ul
        lis = d.find_all('li', class_='')
    else:
        lis = div.find_all('li', class_='ewb-info-item')
    data = []
    for li in lis:
        a = li.find("a")
        try:
            title = a['title'].strip()
        except:
            title = a.text.strip()
        link = a["href"]
        if 'http' in link:
            href = link
        else:
            href = 'http://cgw.xjbt.gov.cn' + link
        if li.find("span", class_='ewb-date'):
            span = li.find("span", class_='ewb-date').text.strip()
        else:
            span = li.find("span", class_='fr').text.strip()
        tmp = [title, span, href]
        data.append(tmp)
    df = pd.DataFrame(data=data)
    df['info'] = None
    return df



def f2(driver):
    locator = (By.XPATH, "//ul[@class='ewb-info-items']/li[last()]//a | //div[@class='con']/ul/li[last()]//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    try:
        locator = (By.XPATH, "//td[@height='18']")
        txt = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
        num = re.findall(r'/(\d+)页', txt)[0]
    except:
        num = 1
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@id='y_detail_con'][string-length()>100]")
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

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
    div = soup.find('div', id='y_detail_con').parent
    return div


data = [
    ["qycg_zhaobiao_benji_gg",
     "http://cgw.xjbt.gov.cn/cggg/bjcggg/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'diqu':'兵团本级'}), f2],
    #
    ["qycg_biangeng_benji_gg",
     "http://cgw.xjbt.gov.cn/cggg/bjgzgg/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'diqu':'兵团本级'}), f2],

    ["qycg_zhongbiao_benji_gg",
     "http://cgw.xjbt.gov.cn/cggg/bjcjgg/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'diqu':'兵团本级'}), f2],
    # # # # ####
    ["qycg_zhongzhi_benji_gg",
     "http://cgw.xjbt.gov.cn/cggg/bjfbzzgg/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'diqu':'兵团本级'}), f2],
    #
    ["qycg_gqita_bian_cheng_benji_gg",
     "http://cgw.xjbt.gov.cn/cggg/bjcqjd/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'diqu':'兵团本级'}), f2],
    #
    ["qycg_zhaobiao_shishi_gg",
     "http://cgw.xjbt.gov.cn/cggg/sscggg/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'diqu':'师市'}), f2],
    #
    ["qycg_biangeng_shishi_gg",
     "http://cgw.xjbt.gov.cn/cggg/ssgzgg/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'diqu':'师市'}), f2],

    ["qycg_zhongbiao_shishi_gg",
     "http://cgw.xjbt.gov.cn/cggg/sscjgg/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'diqu':'师市'}), f2],
    # # # # ####
    ["qycg_liubiao_shishi_gg",
     "http://cgw.xjbt.gov.cn/cggg/ssfbzzgg/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1,{'diqu':'师市'}), f2],

    ####
    #
    ["qycg_dyly_benji_gg",
     "http://cgw.xjbt.gov.cn/xxgk/dyly/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '兵团本级'}), f2],
    #
    ["qycg_dyly_shishi_gg",
     "http://cgw.xjbt.gov.cn/xxgk/ssdyly/index.shtml",
     ["name", "ggstart_time", "href", "info"], add_info(f1, {'diqu': '师市'}), f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="兵团政府采购", **args)
    est_html(conp, f=f3, **args)


if __name__ == '__main__':
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "cgw_xjbt_gov_cn"])

    #
    # for d in data[-3:]:
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


