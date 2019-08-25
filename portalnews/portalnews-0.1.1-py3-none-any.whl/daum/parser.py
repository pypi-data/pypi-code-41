import lxml.html
from io import StringIO

def get_data_client_id(r):
    tree = lxml.html.fromstring(r.text)
    item = tree.get_element_by_id('alex-area')
    return item.get('data-client-id')

def parse_ranking(r):
    page = StringIO(r.text)
    html = ''
    for line in page:
        if line.endswith('<ul class=\"list_news2\">\n'):
            while not line.endswith('</ul>\n'):
                html += line
                line = next(page)
            html += line

    tree = lxml.html.fragment_fromstring(html)

    def parse_li(li):
        a = li.find('.//a[@class="link_txt"]')
        href = a.get('href')
        title = a.text
        office = li.find('.//span[@class="info_news"]').text
        summary = li.find('.//span[@class="link_txt"]').text.strip()
        artc = dict(url=href, title=title, office=office, summary=summary)

        try:
            artc['comment_count'] = int(li.find('.//span[@class="ico_news2"]').text.replace(',', ''))
        except AttributeError:
            pass

        return artc

    return [parse_li(li) for li in tree]

def parse_newsbox(r):
    tree = lxml.html.fromstring(r.text)
    items = tree.xpath('//*[@id="mArticle"]/div[2]/ul/li[not(@class)]')
    artcs = []

    try:
        paging = tree.xpath('//*[@id="mArticle"]/div[2]/div/span')[0]
        is_last_page = (list(paging)[-1].tag == 'em')
    except (IndexError, TypeError):
        is_last_page = True

    for t in items:
        url = t.find('.//a').get('href')
        title = t.find('.//a').text
        office = t.find('span[@class="info_news"]').text
        artc = dict(url=url, title=title, office=office)
        artcs.append(artc)

    return artcs, is_last_page

def parse_breakingnews(r):
    def parse_item(item):
        url = item.find('div/strong/a').get('href').strip()
        title = (item.find('div/strong/a').text or '').strip()
        office = item.find('.//span[@class="info_news"]').text.strip()
        timestamp = item.find('.//span[@class="info_time"]').text.strip()
        summary = item.find('div/div/span').text.strip().strip()
        return dict(url=url, timestamp=timestamp, office=office, title=title, summary=summary)

    tree = lxml.html.fromstring(r.text)
    main = tree.find('.//*[@id="mArticle"]')
    items = main.xpath('div[@class="box_etc"]/ul/li')
    articles = [parse_item(li) for li in items]

    try:
        paging = main.xpath('div[@class="box_etc"]/div[@class="paging_news"]/span/*')
        is_last_page = paging[-1].tag == 'em'
    except IndexError:
        is_last_page = True

    return articles, is_last_page


def parse_ranking_item(elem):
    url = elem.find('.//a[@class="link_txt"]').get('href')
    title = elem.find('.//a[@class="link_txt"]').text.strip()
    office = elem.find('.//span[@class="info_news"]').text
    summary = elem.find('.//span[@class="link_txt"]').text.strip()


def parse_ranking_page(resp):
    tree = lxml.html.fromstring(resp.text)
    temp = tree.xpath('.//ul[@class="list_news2"]/li')


if __name__ == '__main__':
    import requests
    from pprint import pprint
    r = requests.get('https://media.daum.net/breakingnews/digital/game?regDate=20190623&page=2')
    l = parse_breakingnews(r)
    pprint(l)