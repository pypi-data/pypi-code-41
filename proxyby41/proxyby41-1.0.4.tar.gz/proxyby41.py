import requests
from bs4 import BeautifulSoup
from time import sleep
import os

user_agent = ["Mozilla/5.0 (platform; rv:geckoversion) Gecko/geckotrail Firefox/firefoxversion"]
url_list_https = "https://api.proxyscrape.com?request=getproxies&proxytype=http&timeout=10000&country=all&ssl=all&anonymity=all"
url_list_socks4 = "https://api.proxyscrape.com?request=getproxies&proxytype=socks4&timeout=10000&country=all"
url_list_socks5 = "https://api.proxyscrape.com?request=getproxies&proxytype=socks5&timeout=10000&country=all"


class scrape_proxy:

    def __init__(self):
        print('')

    @staticmethod
    def http():
        sleep(2)
        print('\n\nStarting Scraping Proxies....')
        r = requests.get(url_list_https)

        with open('proxy_http.txt', 'wb+') as f:
            f.write(r.content)
            f.close()
        sleep(2)

        url2 = 'https://www.proxy-list.download/api/v1/get?type=https'
        url1 = 'https://www.proxy-list.download/api/v1/get?type=http'
        l = requests.get(url2)
        ll = requests.get(url1)
        with open('proxy_http.txt', 'ab+') as w:
            w.write(l.content)
            w.write(ll.content)
            w.close()

        urll = 'https://www.proxy-daily.com/'
        r = requests.get(urll).text
        soup = BeautifulSoup(r, features='html.parser')
        k = soup.find('div', {'class': 'centeredProxyList freeProxyStyle'})
        rep = str(k).replace('<div class="centeredProxyList freeProxyStyle">', '')
        rep = rep.replace('</div>', '')
        with open('proxy_http.txt', 'a') as ww:
            ww.writelines(rep)
            ww.close()

        print('Leeching Done Successfully')
        sleep(2)

        print('Removing Duplicates...')

        sleep(1)

        uniq_lines = set(open('proxy_http.txt').readlines())

        open('proxy_https.txt', 'w').writelines(set(uniq_lines))

        with open('proxy_https.txt', 'r') as f:
            print('Total Http/Https Proxies Available: ', len(f.readlines()))

        os.system('rm proxy_http.txt')

    @staticmethod
    def socks4():
        sleep(2)
        print('\n\nStarting Scraping Socks4 Proxies...')
        r = requests.get(url_list_socks4)

        with open('proxy_socks4.txt', 'wb+') as f:
            f.write(r.content)
            f.close()

        url = 'https://www.proxy-list.download/api/v1/get?type=socks4'
        rr = requests.get(url)

        with open('proxy_socks4.txt', 'ab+') as ff:
            ff.write(rr.content)
            ff.close()

        sleep(2)

        urll = 'https://www.proxy-daily.com/'
        r = requests.get(urll).text
        soup = BeautifulSoup(r, features='html.parser')
        k = soup.find('div', {'class': 'centeredProxyList freeProxyStyle'})
        rep = str(k).replace('<div class="centeredProxyList freeProxyStyle">', '')
        rep = rep.replace('</div>', '')
        with open('proxy_socks4.txt', 'a') as ww:
            ww.writelines(rep)
            ww.close()

        print('Removing Duplicates Please Wait')
        sleep(2)

        uniq_lines = set(open('proxy_socks4.txt').readlines())

        open('proxy_socks4.txt', 'w').writelines(set(uniq_lines))

        with open('proxy_socks4.txt', 'r') as f:
            print('Total Socks4 Proxies Available: ', len(f.readlines()))

    @staticmethod
    def socks5():
        sleep(2)
        print('\n\nStarting Scraping Socks5 Proxies')
        r = requests.get(url_list_socks5)

        with open('proxy_socks5.txt', 'wb+') as f:
            f.write(r.content)
            f.close()

        url = 'https://www.proxy-list.download/api/v1/get?type=socks5'
        rr = requests.get(url)

        with open('proxy_socks5.txt', 'ab+') as ff:
            ff.write(rr.content)
            ff.close()

        sleep(2)

        print('Removing Duplicates Please Wait')
        sleep(2)

        uniq_lines = set(open('proxy_socks5.txt').readlines())

        open('proxy_socks5.txt', 'w').writelines(set(uniq_lines))

        with open('proxy_socks5.txt', 'r') as f:
            print('Total Socks5 Proxies Available: ', len(f.readlines()))

    @staticmethod
    def get_all():
        scrape_proxy.http()
        scrape_proxy.socks4()
        scrape_proxy.socks5()
