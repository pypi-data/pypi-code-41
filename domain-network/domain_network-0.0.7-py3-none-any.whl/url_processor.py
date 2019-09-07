import re
import requests
import os
from domain_network_utils import save_dataframe
from urllib.parse import urlsplit


def _redirect_link(url):
    try:
        r = requests.head(url, timeout=1, allow_redirects=True)
        print(r.url)
        return r.url
    except Exception:
        return url


def _clean_netloc(text):
    text = re.sub(r"www.", "", text, flags=re.MULTILINE)
    return text

def _clean_netlocs(df):
    """ add a column with the clean_netloc, 'www.' is removed, to the data """
    df['url_netloc_clean'] = df['url_netloc'].apply(_clean_netloc)
    return df


def _get_redirect_links(df_urls, shortened_urls_to_redirect):
    """ update column expanded_url with the redirect link
       Takes too much time, if we want to apply it for all
    """
    df_urls['expanded_url_redirected'] = df_urls.loc[df_urls['url_netloc_clean'].isin(shortened_urls_to_redirect),\
                      'expanded_url'].apply(_redirect_link)

    df_urls.loc[~df_urls['expanded_url_redirected'].isnull(),'expanded_url'] = \
            df_urls.loc[~df_urls['expanded_url_redirected'].isnull(),'expanded_url_redirected']
    return df_urls

def _extract_netloc(df):
    ''' add a column with the netloc to the data'''
    df['url_netloc'] = df['expanded_url'].apply(lambda x: urlsplit(x).netloc)
    return df


def process_urls(df_urls, url_shortener_list, processed_output_file):

    df_urls = _extract_netloc(df_urls)

    df_urls = _clean_netlocs(df_urls)

    df_urls = _get_redirect_links(df_urls, url_shortener_list)

    """repeat for new redirected links"""
    df_urls = _extract_netloc(df_urls)

    """repeat for new redirected links"""
    df_urls = _clean_netlocs(df_urls)

    save_dataframe(df_urls, processed_output_file)

    return df_urls