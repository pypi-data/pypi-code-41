import requests, urllib.parse
from bs4 import BeautifulSoup


class Py1337x:

    def __init__(self):
        self.base_url = "https://1337x.to"
        self.path_search = "/search/"
        self.path_sort_search  = "/sort-search/"
        self.headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}

    def search(self, query, sort_by='', removeZeroSeeds=True, smallToLargeTorrents=True):
        '''
            Returns a List of Torrents 

            Parameters:
            query (str): Torrent to search
            sort_by (str): Sorts the list by the following values
                            'time/desc' : Time Descending,
                            'time/asc' : Time Ascending,
                            'size/desc' : Size Descending,
                            'size/asc' : Size Ascending,
                            'seeders/desc' : Size Descending
                            'seeders/asc' : Seeders Ascending
                            'leechers/desc': Leechers Descending
                            'leechers/asc': Leechers Ascending
            removeZeroSeeds(bool): Default -  True = Removes zero seed torrents
            smallToLargeTorrents(bool): Default - True = Sorts current list by small to large size torrents

            Returns:
            data(list): List of Torrents
        '''
        
        data = []
        
        page_number = "1"

        if sort_by == '':
            query_encoded = urllib.parse.quote_plus(query)
            url = "{0}{1}{2}/{3}/".format(self.base_url, self.path_search, query_encoded, page_number)
        else:
            query_encoded = urllib.parse.quote(query)
            url = "{0}{1}{2}/{3}/{4}/".format(self.base_url, self.path_sort_search, query_encoded, sort_by, page_number)
        
        page = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(page.content, 'html.parser')
        
        table_rows = soup.findAll("tr")

        for row in table_rows:
            if row.find("th") is None:
                page_link = row.find("td", {"class": "coll-1"}).findAll("a")[1]['href']
                torrent_data = self.get_torrent_data(page_link, removeZeroSeeds)
                if torrent_data != {}:
                    data.append(torrent_data)
        if (smallToLargeTorrents):
            return self.sort_torrents_by_size(data)
        else:
            return data
                

    def get_torrent_data(self, page_link, removeZeroSeeds=True):
        torrent_data = {}

        url = "{0}{1}".format(self.base_url, page_link)
        page = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(page.content, 'html.parser')

        torrent_title = soup.find("h1").text.strip()
        list_items = soup.findAll("li")
        for item in list_items:
            anchor = item.find("a")
            if anchor is not None and anchor.text == "Magnet Download":
                magnet_link = anchor['href']
                break
            
        #magnet_link = soup.find("", {"class": "lf1f7478c19b56177c13a1c87624f358cada2229d lcdbc4154475fa2d12676875bd285cb3fd63f8115 lb2a51dca0a954ab424fc98711612dd74f2eb3435"})['href']
        meta_data = soup.findAll("ul", {'class': 'list'})[1:]

        for data in meta_data:
            for li in data.findAll("li"):
                if li.find("strong").text == "Total size":
                    size_split = li.find("span").text.split(" ")
                    if size_split[1] == "GB":
                        size_split[0] = float(size_split[0])*1024
                    elif size_split[1] == "MB":
                        size_split[0] = float(size_split[0])
                    elif size_split[1] == "KB":
                        size_split[0] = float(size_split[0])/1024
                    torrent_data["Total_size_in_MB"] = size_split[0]
                    
                torrent_data[li.find("strong").text] = li.find("span").text

        torrent_data['MagnetLink'] = magnet_link
        torrent_data['title'] = torrent_title

        if (torrent_data['Seeders'] == "0") and (removeZeroSeeds):
            return {}
        else:
            return torrent_data

    def sort_torrents_by_size(self, data):
        # Removes Torrents with 0 Seeders and Sorts the torrents list
        return sorted(data, key=lambda k: k['Total_size_in_MB']) 

        




        
