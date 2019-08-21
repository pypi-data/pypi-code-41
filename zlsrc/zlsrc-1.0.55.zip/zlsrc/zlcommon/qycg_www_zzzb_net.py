import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zlsrc.util.etl import est_html, est_meta, add_info
import time




def f1(driver, num):
    locator = (By.XPATH, "//div[@class='new_b'][last()]/div//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()

    locator = (By.XPATH, "//span[@id='Label3']")
    cnum = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()

    if int(cnum) != int(num):
        val = driver.find_element_by_xpath("//div[@class='new_b'][last()]/div//a").get_attribute('href')[-25:]
        driver.find_element_by_xpath("//input[@id='TextBox1']").clear()
        driver.find_element_by_xpath("//input[@id='TextBox1']").send_keys(num)
        driver.find_element_by_xpath("//a[@id='LinkButton5']").click()

        locator = (By.XPATH, '//div[@class="new_b"][last()]/div//a[not(contains(@href,"%s"))]'%(val))
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))

    data = []
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    lis = soup.find_all('div', class_='new_b')
    url = driver.current_url
    for tr in lis:
        a = tr.find('a', class_='fl')
        try:
            name = a['title']
        except:
            name = a.text.strip()

        if 'http' in a['href']:
            href = a['href']
        else:
            href = 'http://www.zzzb.net/' + a['href']
        ggstart_time = tr.find('span', class_='fr').text.strip()
        temp = [name, ggstart_time, href]
        data.append(temp)

    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


def f2(driver):
    locator = (By.XPATH, "//div[@class='new_b'][last()]/div//a")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()

    locator = (By.XPATH, "//span[@id='Label4']")
    total_page = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    driver.execute_script('javascript:WebForm_DoPostBackWithOptions(new WebForm_PostBackOptions("LinkButton4", "", true, "", "", false, true))')
    for i in range(int(total_page)):
        try:
            locator = (By.XPATH, "//div[@class='new_b'][last()]/div//a")
            WebDriverWait(driver, 2).until(EC.presence_of_element_located(locator)).text.strip()
            break
        except:
            driver.execute_script('javascript:WebForm_DoPostBackWithOptions(new WebForm_PostBackOptions("LinkButton2", "", true, "", "", false, true))')

    locator = (By.XPATH, "//span[@id='Label3']")
    num = WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).text.strip()
    driver.quit()
    return int(num)


def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, "//div[@class='content'][string-length()>60]")
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
    div=soup.find('div',class_='new_right')
    if div == None:raise ValueError
    return div


data = [
    ["qycg_zhaobiao_gg",
     "http://www.zzzb.net/list.aspx?newstype=1003",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["qycg_zhongbiaohx_gg",
     "http://www.zzzb.net/list.aspx?newstype=1005",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]




def work(conp, **args):
    est_meta(conp, data=data, diqu="中资国际工程咨询集团", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    work(conp=["postgres", "since2015", "192.168.3.171", "zlest1", "www_zzzb_net"])


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
    #     for f in df[2].values:
    #         d = f3(driver, f)
    #         print(d)
