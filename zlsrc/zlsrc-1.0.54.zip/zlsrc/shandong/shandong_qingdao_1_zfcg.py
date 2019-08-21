
import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from zlsrc.util.fake_useragent import UserAgent
from zlsrc.util.etl import est_html, est_meta, add_info, est_meta_large
import time


ua = UserAgent()

headers = {

    'User-Agent': ua.random,
}


def get_ip():
    global proxy
    try:
        url = """http://ip.11jsq.com/index.php/api/entry?method=proxyServer.generate_api_url&packid=0&fa=0&fetch_key=&qty=1&time=1&pro=&city=&port=1&format=txt&ss=1&css=&dt=1&specialTxt=3&specialJson="""
        r = requests.get(url)
        time.sleep(1)
        ip = r.text
        proxy = {'http': ip}
    except:
        proxy = {}
    return proxy


def get_response(driver, url, param_data):
    proxy = {}
    driver_info = webdriver.DesiredCapabilities.CHROME
    try:
        if "--proxy" in driver_info['goog:chromeOptions']['args'][0]:
            proxy_ip = driver_info['goog:chromeOptions']['args'][0].split('=')[1].split('://')
            proxies = {proxy_ip[0]: proxy_ip[1]}
            page = requests.post(url, data=param_data, proxies=proxies, headers=headers, timeout=50).text
        else:
            if proxy == {}: get_ip()
            page = requests.post(url, data=param_data, headers=headers, timeout=50, proxies=proxy).text
    except:
        try:
            page = requests.post(url, data=param_data, headers=headers, timeout=50, proxies=proxy).text
        except:
            get_ip()
            page = requests.post(url, data=param_data, headers=headers, timeout=50, proxies=proxy).text

    return page


def f1(driver, num):
    flag = driver.current_url.rsplit('&', 1)[-1]
    payload = 'callCount=1\nwindowName=\nc0-scriptName=dwrmng\nc0-methodName=queryWithoutUi\nc0-id=0\nc0-param0=number:7\nc0-e1=string:0401\nc0-e2=string:66\nc0-e3=number:10\nc0-e4=string:\nc0-e5=null:null\nc0-param1=Object_Object:{_COLCODE:reference:c0-e1, _INDEX:reference:c0-e2, _PAGESIZE:reference:c0-e3, _REGION:reference:c0-e4, _KEYWORD:reference:c0-e5}\nbatchId=2\npage=%2Fsdgp2014%2Fsite%2Fchannelall370200.jsp%3Fcolcode%3D0401%26flag%3D0401\nhttpSessionId=\nscriptSessionId=0DEEA2557D3A53176D75C32ADC566925'
    new_payload1 = re.sub('c0-e1=string:0401', 'c0-e1=string:' + flag, payload)
    new_payload = re.sub('c0-e2=string:66', 'c0-e2=string:' + str(num), new_payload1)
    res = get_response(driver, 'http://zfcg.qingdao.gov.cn/sdgp2014/dwr/call/plaincall/dwrmng.queryWithoutUi.dwr', new_payload).encode(
        'utf-8').decode('unicode_escape')
    rslt = re.findall('"([^"]*?)"', res)[-1].split('?')
    data = []

    for rs in rslt:
        split_list = rs.split(',')
        ggstart_time = split_list[2]

        name = split_list[1]

        url = 'http://zfcg.qingdao.gov.cn/sdgp2014/site/read' + split_list[3] + '.jsp?id=' + split_list[0] + '&flag=' + flag
        # url = driver.current_url.rsplit('/', 1)[0] + rs.xpath("./td/a/@href")[0].strip('.')
        temp = [name, ggstart_time, url]
        data.append(temp)

    df = pd.DataFrame(data=data)
    df['info'] = None
    return df


tag = {
    '0401': '采购公告',
    '0402': '中标公告',
    '0403': '更正公告',
    '0404': '废标公告',
    '0405': '单一来源',
}


def jumTag(driver, tag_code):
    text = tag[tag_code]

    locator = (By.XPATH, "//ul[@id='tags']/li/a[contains(text(),'%s')]" % text)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator)).click()


def f2(driver):
    flag = driver.current_url.rsplit('&', 1)[-1]
    jumTag(driver,flag)
    time.sleep(0.1)
    while 1:
        try:
            locator = (By.XPATH, '//a[@id="back" and @class=""]')
            WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).click()
        except Exception as e:

            break

    locator = (By.XPATH, '//a[@name="pagenum"][last()]')
    total_page = WebDriverWait(driver, 30).until(EC.presence_of_element_located(locator)).text
    driver.quit()
    return int(total_page)




def f3(driver, url):
    driver.get(url)
    locator = (By.XPATH, '//div[@class="neiright"]')
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(locator))
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
    div = soup.find('div', class_='neiright')
    return div


data = [
    ["zfcg_zhaobiao_gg",
     "http://zfcg.qingdao.gov.cn/sdgp2014/site/channelall370200.jsp?colcode=0401&flag=0401&0401",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_zhongbiao_gg",
     "http://zfcg.qingdao.gov.cn/sdgp2014/site/channelall370200.jsp?colcode=0401&flag=0401&0402",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_biangeng_gg",
     "http://zfcg.qingdao.gov.cn/sdgp2014/site/channelall370200.jsp?colcode=0401&flag=0401&0403",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_liubiao_gg",
     "http://zfcg.qingdao.gov.cn/sdgp2014/site/channelall370200.jsp?colcode=0401&flag=0401&0404",
     ["name", "ggstart_time", "href", "info"], f1, f2],

    ["zfcg_dyly_gg",
     "http://zfcg.qingdao.gov.cn/sdgp2014/site/channelall370200.jsp?colcode=0401&flag=0401&0405",
     ["name", "ggstart_time", "href", "info"], f1, f2],

]


def work(conp, **args):
    est_meta(conp, data=data, diqu="山东省青岛市", **args)
    est_html(conp, f=f3, **args)


if __name__ == "__main__":
    conp = ["postgres", "since2015", "192.168.3.171", "zlsrc", "zfcg_shandong_qingdao"]
    # driver = webdriver.Chrome()
    # driver.get('http://zfcg.qingdao.gov.cn/sdgp2014/site/channelall370200.jsp?colcode=0401&flag=0401&0401')
    # f2(driver)
    # f1(driver, 3)
    work(conp, )
    # for d in data:
    #     driver = webdriver.Chrome()
    #     driver.get(d[1])
    #     total = f2(driver)
    #     print(total)
    #     driver = webdriver.Chrome()
    #     # i =  random.randint(1,total)
    #     driver.get(d[1])
    #     print(d[1])
    #     for i in range(1,total):
    #         df_list = f1(driver, i).values.tolist()
    #         # print(df_list[:10])
    #         # df1 = random.choice(df_list)
    #         # print(str(f3(driver, df1[2]))[:100])
    #     driver.quit()
