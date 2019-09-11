from .model import Anime

import requests
from bs4 import BeautifulSoup

import time
import sys
from multiprocessing import Pool


class MALScraper:
    """Scrapes https://myanimelist.net/ using BeautifulSoup4.

    Methods
    -------
    get_anime(anime), get_anime_url(anime)
    """

    def __init__(self):
        # MAL search url
        self.MAL_URL = 'https://myanimelist.net/anime.php?q='
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0'
        }

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

        res = requests.get(url, headers=self.headers)
        while res.status_code != 200:
            time.sleep(1)
            res = requests.get(url, headers=self.headers)

        soup = BeautifulSoup(res.text, features='lxml')
        lnk = None
        try:
            a = soup.find('a', {'class': 'hoverinfo_trigger fw-b fl-l'})
            lnk = a['href']
        except Exception as e:
            print(f'Error getting anime url.\nError: {e}')
        return lnk

    def get_all_anime(self, start=0, to=16100):
        """Gets all the anime from the website. Each anime has kind of index based pointer.

        Parameters
        ----------
        start : int
            Start point of the anime. Starts at 0.
        to : int
            End point of the anime. Ends at 16100.

        Returns
        -------
        str
            Returns the anime url link.
        """
        if to % 50 != 0 or to > 16100:
            raise ValueError(
                'Value of parameter to must be divisible by 50, or less than or equal to 16100.')

        total_anime = to
        count = start
        url = 'https://myanimelist.net/topanime.php?limit={count}'
        links = []

        while count <= total_anime:
            res = requests.get(url, headers=self.headers)

            while res.status_code != 200:
                time.sleep(1)
                res = requests.get(url, headers=self.headers)

            soup = BeautifulSoup(res.text, features='lxml')

            try:
                aa = soup.find_all(
                    'a', {'class': 'hoverinfo_trigger fl-l fs14 fw-b'})

                for a in aa:
                    link = a['href']

                    if link:
                        links.append(link)
                        print(f'Link count: {len(links)}')
            except Exception as e:
                print(e)

            count += 50

        sys.setrecursionlimit(25000)
        p = Pool(10)
        animes = p.map(Anime, links)
        p.terminate()
        p.join()

        return animes
