from bs4 import BeautifulSoup
import requests
import time
from fake_useragent import UserAgent

def get_ip(mode='http'):
    try:
        ua = UserAgent()
    except:
        ua = UserAgent()
    baseurl = 'https://www.xicidaili.com/wt/'
    if mode == 'https':
        baseurl = 'https://www.xicidaili.com/wn/'
    ip_list = []
    for i in range(2,11):
        headers = {
            'User-Agent': ua.random
        }
        url = baseurl + str(i)
        web_data = requests.get(url, headers=headers)
        soup = BeautifulSoup(web_data.text, 'lxml')
        ips = soup.find_all('tr')
        ip_list = []
        for i in range(1, len(ips)):
            ip_info = ips[i]
            tds = ip_info.find_all('td')
            ip_list.append('http://'+tds[1].text + ':' + tds[2].text)
            print('http://'+tds[1].text + ':' + tds[2].text)

        time.sleep(2)
    text = '\n'.join(ip_list)
    f = open('ip.txt', 'w')
    f.write(text)
    f.close()

if __name__ == '__main__':
    get_ip()





