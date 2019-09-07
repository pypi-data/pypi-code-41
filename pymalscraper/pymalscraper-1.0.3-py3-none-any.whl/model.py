import time
import requests
from bs4 import BeautifulSoup


class Anime:
    def __init__(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0'
        }
        res = requests.get(url, headers=headers)
        while res.status_code != 200:
            time.sleep(1)
            res = requests.get(url, headers=headers)

        self.soup = BeautifulSoup(res.text, features='lxml')

    @property
    def title(self):
        title = None

        try:
            span = self.soup.find('span', {'itemprop': 'name'})
            title = span.text
        except Exception as e:
            print(f'Error getting title.\nError: {e}')

        return title

    @property
    def english_title(self):
        english_title = None

        try:
            divs = self.soup.find_all('div', {'class': 'spaceit_pad'})

            for div in divs:
                if 'English:' in div.text:
                    english_title = div.text.replace(
                        'English:', '').rstrip().lstrip()
                    break
        except Exception as e:
            print(f'Error getting english title.\nError: {e}')

        return english_title

    @property
    def japanese_title(self):
        japanese_title = None

        try:
            divs = self.soup.find_all('div', {'class': 'spaceit_pad'})

            for div in divs:
                if 'Japanese:' in div.text:
                    japanese_title = div.text.replace(
                        'Japanese:', '').rstrip().lstrip()
                    break
        except Exception as e:
            print(f'Error getting japanese title.\nError: {e}')

        return japanese_title

    @property
    def synonyms(self):
        synonyms = None

        try:
            divs = self.soup.find_all('div', {'class': 'spaceit_pad'})

            for div in divs:
                if 'Synonyms:' in div.text:
                    synonyms = div.text.replace(
                        'Synonyms:', '').rstrip().lstrip()
                    break
        except Exception as e:
            print(f'Error getting synonyms.\nError: {e}')

        return synonyms

    @property
    def synopsis(self):
        synopsis = None

        try:
            span = self.soup.find('span', {'itemprop': 'description'})
            synopsis = span.text
        except Exception as e:
            print(f'Error getting synopsis.\nError: {e}')

        return synopsis

    @property
    def animetype(self):
        mtype = None

        try:
            divs = self.soup.find(
                'div', {'class': 'js-scrollfix-bottom'}).find_all('div')

            for div in divs:
                if 'Type:' in div.text:
                    mtype = div.text.replace('Type:', '').rstrip().lstrip()
                    break
        except Exception as e:
            print(f'Error getting type.\nError: {e}')

        return mtype

    @property
    def episodes(self):
        eps = None

        try:
            divs = self.soup.find(
                'div', {'class': 'js-scrollfix-bottom'}).find_all('div', {'class': 'spaceit'})

            for div in divs:
                if 'Episodes:' in div.text:
                    eps = div.text.replace('Episodes:', '').rstrip().lstrip()
                    break
        except Exception as e:
            print(f'Error getting episodes.\nError: {e}')

        return eps

    @property
    def genres(self):
        genres = None

        try:
            divs = self.soup.find(
                'div', {'class': 'js-scrollfix-bottom'}).find_all('div')

            for div in divs:
                if 'Genres:' in div.text:
                    genres = div.text.replace('Genres:', '').rstrip().lstrip()
                    break
        except Exception as e:
            print(f'Error getting genres.\nError: {e}')

        return genres

    @property
    def poster(self):
        poster = None

        try:
            img = self.soup.find('img', {'class': 'ac'})
            poster = img['src']
        except Exception as e:
            print(f'Error getting poster.\nError: {e}')

        return poster

    @property
    def trailer(self):
        trailer = None

        try:
            a = self.soup.find(
                'a', {'class': 'iframe js-fancybox-video video-unit promotion'})
            trailer = a['href']
        except Exception as e:
            print(f'Error getting trailer.\nError: {e}')

        return trailer
