import hy.macros
from hy.core.language import butlast, first, last, merge_with, rest
import requests
from selectolax.parser import HTMLParser
from readability import Document
from anarcute.lib import *
hy.macros.require('anarcute.lib', None, assignments='ALL', prefix='')
oferta_template = 'https://allegro.pl/oferta/{}'
TIMEOUT = 10
TOYS_CATEGORIES = ['Dziecko', 'Gry', 'Towarzyskie', 'Gadzety',
    'Modelarstwo', 'Sport i turystyka', 'Maskotki', 'Moda',
    'Akcesoria do zabawek', 'Książki i Komiksy', 'Zabawki',
    'Kolekcje i sztuka', 'Kultura i rozrywka']
CATEGORIES = TOYS_CATEGORIES


def filter_category(res, cat):
    if 'items' in res:
        best = list(filter(res['items']))
        _hy_anon_var_1 = best if best else first(res['items'])
    else:
        _hy_anon_var_1 = []
    return _hy_anon_var_1


def categories_of(item):
    return (lambda arr: list(map(lambda x: x['name'], arr)))((lambda arr:
        list(filter(lambda x: 'name' in x, arr)))(item['pagemap']['listitem'])
        ) if 'pagemap' in item and 'listitem' in item['pagemap'] else []


def is_category(item, cat):
    return in_or(cat if type(cat) in [list, tuple] else [cat],
        categories_of(item))


def is_oferta(item):
    return 'link' in item and 'oferta' in item[link]


def is_for_kids(breadcrumbs):
    return in_or(breadcrumbs, ','.join(CATEGORIES))


def parse_atts(lax):
    atts = {}
    for li in (lambda arr: list(map(lambda x: x.text(), arr)))(lax.css(
        '.app-container li li')):
        k = first(li.split(':', 1))
        v = last(li.split(':', 1))
        atts[k] = v
    return atts


def parse_atts_deprecated(lax):
    return dict(zip((lambda arr: list(map(lambda hyx_Xpercent_signX1:
        hyx_Xpercent_signX1.text(), arr)))(lax.css(
        '.asi-attributes__list dt')), (lambda arr: list(map(lambda
        hyx_Xpercent_signX1: hyx_Xpercent_signX1.text(), arr)))(lax.css(
        '.asi-attributes__list dd'))))


def is_deprecated(lax):
    try:
        header = trim(lax.css_first('h2.container-header').text().replace(
            '\n', ' '))
    except Exception:
        header = ''
    try:
        m_price = lax.css_first('.m-price').text()
    except Exception:
        m_price = ''
    return 'Nie było ofert kupna' in m_price or 'nieaktualna' in header


def parse_description(lax):
    return trim(HTMLParser(Document(lax.css_first(
        '.asi-description__main,.description ').html).summary()).text())


def link_to_id(link):
    return only_numbers(last(first(link.split('?')).split('-')))


def get_page(link, legit=thru, spare=[], timeout=10, session=None, html=False):
    session = session if session else requests
    link = str(link)
    link = oferta_template.format(link) if not 'allegro' in link else link
    try:
        text = session.get(link, headers=headers, timeout=timeout).text
    except Exception:
        text = requests.get(link, headers=headers, timeout=timeout).text
    lax = HTMLParser(text)
    try:
        title = trim(lax.css_first('h1').text().replace('\n', ' '))
    except Exception:
        title = ''
    try:
        header = trim(lax.css_first('h2.container-header').text().replace(
            '\n', ' '))
    except Exception:
        header = ''
    try:
        proposition = lax.css_first('.carousel-item a').attributes['href']
    except Exception:
        proposition = ''
    try:
        breadcrumbs = (lambda arr: list(map(lambda x: x.text(), arr)))(lax.
            css('[data-role=breadcrumbs-list] span'))
    except Exception:
        breadcrumbs = ''
    try:
        description = parse_description(lax)
    except Exception:
        description = ''
    try:
        rating_value = float(lax.css_first('[itemprop=ratingValue]').
            attributes['content'])
    except Exception:
        rating_value = ''
    try:
        rating_count = int(lax.css_first('[itemprop=ratingCount]').
            attributes['content'])
    except Exception:
        rating_count = ''
    try:
        customers_count = first(lax.css_first('[itemprop=offers]').parent.
            css_first('div:contains(osoby),div:contains(osób)').text().
            split(' '))
    except Exception:
        customers_count = ''
    try:
        sales_count = last(butlast(lax.css_first('[itemprop=offers]').
            parent.css_first('div:contains(osoby),div:contains(osób)').text
            ().split(' ')))
    except Exception:
        sales_count = ''
    try:
        img = lax.css_first('[itemprop=image]').attributes['content']
    except Exception:
        img = ''
    if proposition and is_deprecated(lax):
        try:
            lax2 = HTMLParser(session.get(proposition, headers=headers,
                timeout=timeout).text)
        except Exception:
            lax2 = HTMLParser(requests.get(proposition, headers=headers,
                timeout=timeout).text)
        atts = merge_with(lambda a, b: b, parse_atts_deprecated(lax2) if
            is_deprecated(lax2) else parse_atts(lax2),
            parse_atts_deprecated(lax))
    else:
        atts = parse_atts(lax)
    result = {'name': title, 'Aukcja': title, 'ID_Aukcji': link_to_id(link),
        'link': link, 'deprecated': is_deprecated(lax), 'proposition':
        proposition, 'atts': atts, 'breadcrumbs': breadcrumbs, 'for_kids':
        is_for_kids(breadcrumbs), 'description': description,
        'rating_count': rating_count, 'rating_value': rating_value,
        'customers_count': customers_count, 'sales_count': sales_count,
        'img': img}
    if html:
        result['html'] = html
        _hy_anon_var_27 = None
    else:
        _hy_anon_var_27 = None
    return result if legit(result) else get_page(first(spare), legit=legit,
        session=session, spare=list(rest(spare))) if spare else None

