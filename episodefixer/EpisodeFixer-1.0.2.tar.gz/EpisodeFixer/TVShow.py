
# importing logging to log and debug the code
# requests,bs4 for webscraping data from TVDB

import logging
import requests
import os
from bs4 import BeautifulSoup
from .Episode import Episode
from .Rename import renameShow
from .UserInput import userInput
from .Subtitle import embedSubtitles

class TVShow:
    """
    This is the TV Show class. It is the main class for doing stuff with a TV Show.
    """

    def __init__(self):
        """TV Show Initializer
        The showname may need to include the year it first aired in case there are multiple shows with that name.
        I use userInput() function to populate the parameters.
        """
        user_parameters = userInput()
        self.name = user_parameters['Show Name']
        self.directory = user_parameters['Directory']
        self.output_format = user_parameters['Format']
        self.show_url = ""
        self.titles = [['' for j in range(100)] for i in range(100)]
        self.episodes = {}
        logging.debug(f"New TV Show of {self.name} created from folder - {self.directory}")
        self.find_titles()
    
    def find_titles(self):
        """
        This function find the titles for all episodes of a tvshow at once.
        It iterates from 1 to 99 and stores the title dict in titles.
        Whenever it returns an empty season dict, it means there are no more seasons and we stop.
        The search terms is name of the show with terminal spaces removed and intermediate spaces replaced by -
        The URL for the show The Flash 2014 is "https://www.thetvdb.com/series/The-Flash-2014/"
        
        """
        web_host = "https://www.thetvdb.com/series/"
        search_term = (self.name).strip().replace(" ","-")
        self.show_url = f"{web_host}{search_term}"
        
        for i in range(1,100):
            self.find_season_titles(i)
            if self.titles[i][1] == '': #Implies Season returned with no titles
                logging.error(f"Titles not found for Season {i} of {self.name}")
                break        
    
    def find_season_titles(self,season:int):
        """
        This is the main scraping function that I use. The purpose of this function is to find the titles 
        It uses the BeautifulSoup and requests library.
        I use the TVDB's series database for scraping info.
        This webpage is retrieved by using the request.get() and we build a parsetree using BeautifulSoup()
        We use the find function to search throught the parse tree. We search for the table tag and then table body.
        We will store the episode titles in a dict indexed by the episode number.
        findAll() finds all the matches with a given tag inside the tree. 
        
        Arguments:
            season {int} -- The season # whose TV Show needs to be found. 
        """
        logging.debug(f"Constructing URL of {self.name} Season {season} .")
        web_page_url = f"{self.show_url}/seasons/{str(season)}"
        logging.debug(f"Looking up title information at the URL {web_page_url}")
        
        web_page = requests.get(web_page_url)
        try:
            if(web_page is None):
                logging.error(f"Web Page : {web_page_url} Not Found")
            else:
                logging.debug(f"Web Page : {web_page_url} Found. Parsing content")
                soup = BeautifulSoup(web_page.content, 'html5lib')
                table = soup.find('table', attrs = {'id':'translations'})
                if(table is None):
                    logging.error("Table Not Present")
                else:
                    body = table.find('tbody') #The body of the table
                    if(body is None):
                        logging.error("Body Not Present")
                    else:
                        for row in body.findAll('tr'): #The rows
                            episode_num = row.find('a') #First row is index i.e. episode number.
                            episode_name = row.find('span', attrs = {'data-language':'en'}) #To retrieve english version of the Title
                            if((episode_name is None) and (episode_num is None)):
                                logging.error("Incomplete Information in Rows")
                            else:
                                ep_num = int(episode_num.text.strip())
                                ep_title = episode_name.text.strip()
                                self.titles[season][ep_num] = ep_title #Storing entry in dict.
                                logging.debug(f"{ep_num} -> {ep_title}")
        except Exception as e:
            logging.exception(f"season {season} raised {repr(e)}")
        
    def rename(self):
        """This is the master function for scanning the Show's Folder and then Renaming it.
        We use os.walk() as it gives us all files and subfolders inside the main folder.
        """
        for root,dirs,files in os.walk(self.directory):
            for name in files:
                path_name = os.path.join(root, name)
                try:
                    # We create an instance of the episode class. 
                    episode = Episode(self.name,path_name,self.directory,self.output_format)
                    if episode.isVideo:
                        episode.episode_title = self.titles[episode.season][episode.episode]
                        episode_info = episode.getRenameDetails()
                        # We only add it to episodes if Path Name has actually changed
                        if episode_info['old']['Path Name']!=episode_info['new']['Path Name']:
                            self.episodes[episode.ID()] = episode_info
                
                # Primitive Exception Handling. Most Errors are unavoidable but a response to User is necessary.
                except Exception as e:
                    logging.exception(f"{path_name} raised {repr(e)}")
        renameShow(self.episodes,self.directory)
    
    def embedShowSubtitles(self):
        """The function embeds Subtitles for all files in the directory.
        os.walk() gives us all files and subfolders inside the main folder and then we call embedSubtitles on them
        """
        
        logging.info(f"Checking the directory : {self.show_directory}")
        for root,__,files in os.walk(self.show_directory):
            for name in files:
                path_name = os.path.join(root, name)
                embedSubtitles(path_name,rm_orig=True)