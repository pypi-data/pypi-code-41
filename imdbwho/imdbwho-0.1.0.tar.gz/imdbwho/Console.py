from .IMDB import *
import json
import urllib.request

class Console:
    prompt = "IMDB>"
    imdb = None

    def __init__(self):
        self.imdb = ImdbSearch()
        return

    def run(self):
        Name = self.GetSearchName()
        people = self.imdb.FindPerson(Name)

        person = None
        if(len(people) > 0):
            if(len(people) == 1):
                #only one person returned so select them
                person = people[0]
            else:
                #multiple people returned so prompt for which one
                person = self.SelectPersonFromList(people)
        else:
            print("no results for %s" % Name)
            return
        
        #print out the movies the person is in
        print("%s\n%s" % (person.Name, person.Bio))
        movies = self.imdb.GetMovies(person.Path)
        self.PrintFilms(movies)

        #ask if wanna save to json file
        print("Save to File? Y / N (default)")
        choice = input(self.prompt)
        if(choice.lower() == 'y'):
            self.SaveToJson(person, movies)

    def GetSearchName(self):
        print("Input a name to search")
        return input(self.prompt)
    
    def SelectPersonFromList(self, people):
        #list all people with index value
        id = 0
        for p in people:
            print("%d.\nName: %s\nBio: %s\n\n" % (id, p.Name, p.Bio))
            id += 1

        #select person by index value
        result = None
        while True:
            print("enter the number of the person to look up")
          
            try:
                ChosenInt = int(input(self.prompt))
                if (ChosenInt < len(people) and ChosenInt > -1):
                    result = people[ChosenInt]
                    break

            except ValueError:
                continue

        return result

    def PrintFilms(self, Films):
        print("What date order would you like films in?\nA: Ascending (default)\nD: Descending")
        choice = input(self.prompt)
        # films are in descending order already so if we get anything but a d reverse the order
        if(choice.lower() != "d"):
            Films.reverse()

        #print out the films
        for film in Films:
           print("%s\t\t%s" % (film.Year, film.Title))

    def SaveToJson(self, Actor, Films):
        #get file path
        print("Enter the file to save to")
        filepath= input(self.prompt)

        #make it pretty
        data = {}
        data["Person"] = Actor._asdict()
        data["Films"] = list()
        for film in Films:
            data["Films"].append(film._asdict())

        try:
            with open(filepath, 'w') as outfile:
                json.dump(data, outfile, indent=4)
        except:
            print("Error writing to file %s. Do you have permissions?" % choice)
