import urllib.request as req
import urllib.parse
from bs4 import BeautifulSoup
import re
import collections

Person = collections.namedtuple('Person', "Name Bio Path")
Film = collections.namedtuple("Film", "Title Year")

class ImdbSearch:
    m_ImdbSearchMovie = "https://www.imdb.com/filmosearch/?explore=title_type&role=%s&sort=year,desc&mode=simple&page=%d&title_type=movie"
    m_ImdbSearchPersonUrl = "https://www.imdb.com/search/name/?name=%s&count=100"

    def __init__(self):
        #add proxy stuff here if u need to
        opener = req.build_opener(req.HTTPHandler)
        req.install_opener(opener)

    def FindPerson(self, Name):
        #send request to build list of people
        url = self.m_ImdbSearchPersonUrl % urllib.parse.quote(Name)
        resp = self.SendRequest(url)

        #find the tags for all returned names in the response
        soup = BeautifulSoup(resp, 'html.parser')
        listerItems = soup.find_all("div", class_="lister-item-content")

        #build result list
        result = list()
        for listerItem in listerItems:
            pElem = listerItem.find_all("p", class_="")
            if (len(pElem) > 0): # some people dont have a bio so we gotta check that
                Bio = pElem[0].text.strip()
            else:
                Bio = None
            
            #clean up and save results
            PersonName = listerItem.a.string.strip()
            Path = listerItem.a['href'][6:].strip() #strip the /name/
            result.append(Person(PersonName, Bio, Path))

        return result

    def GetMovies(self, PersonPath):
        page = 0
        result = list()

        #only 50 shown per page so need to loop
        while True:
            page += 1
            url = self.m_ImdbSearchMovie % (PersonPath, page)
            resp = self.SendRequest(url)

            #no result means we gone over the last page
            if(resp == "" or "No results. Try removing genres, ratings, or other filters to see more." in resp):
                break

            # get list of movies from the response
            soup = BeautifulSoup(resp, 'html.parser')
            films = soup.find_all("span", class_="lister-item-header")
            
            # build dict of movies with the year dict will be in decending order
            for film in films:
                year = film.find("span", class_="lister-item-year text-muted unbold").string
                if(year != None): # if the year is none then the movie has not been released yet
                    years = re.findall("\d{4}", year)
                    if(len(years) > 0):
                        year = years[0]
                    else: # year is in an unkown format or something wierd 
                        year = "Unknown"
                else:
                    year = "TBA"

                result.append(Film(film.a.string.strip(), year))

        return result

    def SendRequest(self, URL):
        result = ""
        try:
            conn = req.urlopen(URL)
            result = conn.read().decode("utf8")

        except:
            print("error sending request to: %s" % URL)

        return result
