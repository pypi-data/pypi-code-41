from .model import Anime

import requests
from bs4 import BeautifulSoup

import time


class MALScraper:
    """Scrapes https://myanimelist.net/ using BeautifulSoup4.

    Methods
    -------
    get_anime(anime), get_anime_url(anime)
    """

    def __init__(self):
        # MAL search url
        self.MAL_URL = 'https://myanimelist.net/anime.php?q='

    def get_anime(self, anime):
        """Gets the anime model data.

        Parameters
        ----------
        anime : str
            Name of the anime.

        Returns
        -------
        class Anime
            Returns the scraped anime model data.
        """

        # Gets the anime url.
        anime_url = self.get_anime_url(anime)
        #
        return Anime(anime_url)

    def get_anime_url(self, anime):
        """Gets the url of the anime from the website.

        Parameters
        ----------
        anime : str
            Name of the anime.

        Returns
        -------
        str
            Returns the anime url link.
        """
        url = self.MAL_URL + anime
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0'
        }

        res = requests.get(url, headers=headers)
        while res.status_code != 200:
            time.sleep(1)
            res = requests.get(url, headers=headers)

        soup = BeautifulSoup(res.text, features='lxml')
        lnk = None
        try:
            a = soup.find('a', {'class': 'hoverinfo_trigger fw-b fl-l'})
            lnk = a['href']
        except Exception as e:
            print(f'Error getting anime url.\nError: {e}')
        return lnk
