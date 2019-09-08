import time
import requests
from bs4 import BeautifulSoup

from .helpers import checked_data_length


class Anime:
    def __init__(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0'
        }
        res = requests.get(url, headers=headers)
        while res.status_code != 200:
            time.sleep(1)
            res = requests.get(url, headers=headers)

        self._soup = BeautifulSoup(res.text, features='lxml')

    @property
    def title(self):
        title = None

        try:
            span = self._soup.find('span', {'itemprop': 'name'})
            title = span.text
        except Exception as e:
            print(f'Error getting title.\nError: {e}')

        return checked_data_length(title, 100)

    @property
    def english_title(self):
        english_title = None

        try:
            divs = self._soup.find_all('div', {'class': 'spaceit_pad'})

            for div in divs:
                if 'English:' in div.text:
                    english_title = div.text.replace(
                        'English:', '').rstrip().lstrip()
                    break
        except Exception as e:
            print(f'Error getting english title.\nError: {e}')

        return checked_data_length(english_title, 150)

    @property
    def japanese_title(self):
        japanese_title = None

        try:
            divs = self._soup.find_all('div', {'class': 'spaceit_pad'})

            for div in divs:
                if 'Japanese:' in div.text:
                    japanese_title = div.text.replace(
                        'Japanese:', '').rstrip().lstrip()
                    break
        except Exception as e:
            print(f'Error getting japanese title.\nError: {e}')

        return checked_data_length(japanese_title, 150)

    @property
    def synonyms(self):
        synonyms = None

        try:
            divs = self._soup.find_all('div', {'class': 'spaceit_pad'})

            for div in divs:
                if 'Synonyms:' in div.text:
                    synonyms = div.text.replace(
                        'Synonyms:', '').rstrip().lstrip()
                    break
        except Exception as e:
            print(f'Error getting synonyms.\nError: {e}')

        return checked_data_length(synonyms, 200)

    @property
    def synopsis(self):
        synopsis = None

        try:
            span = self._soup.find('span', {'itemprop': 'description'})
            synopsis = span.text
        except Exception as e:
            print(f'Error getting synopsis.\nError: {e}')

        return synopsis

    @property
    def animetype(self):
        atype = None

        try:
            divs = self._soup.find(
                'div', {'class': 'js-scrollfix-bottom'}).find_all('div')

            for div in divs:
                if 'Type:' in div.text:
                    atype = div.text.replace('Type:', '').rstrip().lstrip()
                    break
        except Exception as e:
            print(f'Error getting type.\nError: {e}')

        return checked_data_length(atype, 10)

    @property
    def episodes(self):
        eps = None

        try:
            divs = self._soup.find(
                'div', {'class': 'js-scrollfix-bottom'}).find_all('div', {'class': 'spaceit'})

            for div in divs:
                if 'Episodes:' in div.text:
                    eps = div.text.replace('Episodes:', '').rstrip().lstrip()
                    break
        except Exception as e:
            print(f'Error getting episodes.\nError: {e}')

        return checked_data_length(eps, 5)

    @property
    def genres(self):
        genres = None

        try:
            divs = self._soup.find(
                'div', {'class': 'js-scrollfix-bottom'}).find_all('div')

            for div in divs:
                if 'Genres:' in div.text:
                    genres = div.text.replace('Genres:', '').rstrip().lstrip()
                    break
        except Exception as e:
            print(f'Error getting genres.\nError: {e}')

        return checked_data_length(genres, 400)

    @property
    def poster(self):
        poster = None

        try:
            img = self._soup.find('img', {'class': 'ac'})
            poster = img['src']
        except Exception as e:
            print(f'Error getting poster.\nError: {e}')

        return poster

    @property
    def trailer(self):
        trailer = None

        try:
            a = self._soup.find(
                'a', {'class': 'iframe js-fancybox-video video-unit promotion'})
            trailer = a['href']
        except Exception as e:
            print(f'Error getting trailer.\nError: {e}')

        return trailer

    def get_data(self, format='json'):
        '''Gets the full data of the anime in specified format.'''

        data = None

        if format == 'json':
            data = {
                'title': self.title,
                'english_title': self.english_title,
                'japanese_title': self.japanese_title,
                'synonyms': self.synonyms,
                'synopsis': self.synopsis,
                'type': self.animetype,
                'episodes': self.episodes,
                'genres': self.genres,
                'poster': self.poster,
                'trailer': self.trailer
            }
        else:
            raise ValueError('Parameter format is invalid.')

        return data
