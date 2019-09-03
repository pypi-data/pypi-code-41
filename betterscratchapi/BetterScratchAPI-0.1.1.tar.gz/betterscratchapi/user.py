try:
    import requests
except ModuleNotFoundError:
    exit("Could not import the requests module!")
import warnings

class user:
    # Allow Defining User, Ex. Command: u = user("ScratchToolBox")
    def __init__(self, u):
        self.user = u


    # Get User ID (integer) Ex. 44834297
    def id(self):
        URL = "https://api.scratch.mit.edu/users/" + self.user
        r = requests.get(url = URL)
        data = r.json()
        return data['id']


    # Get User username (string) Ex. ScratchToolBox
    def username(self):
        URL = "https://api.scratch.mit.edu/users/" + self.user
        r = requests.get(url = URL)
        data = r.json()
        return data['username']


    # Get if user is Scratch Team (boolean) Ex. False
    def is_scratchteam(self):
        URL = "https://api.scratch.mit.edu/users/" + self.user
        r = requests.get(url = URL)
        data = r.json()
        return data['scratchteam']


    # Get user's join date (string) Ex. 2019-05-04T17:22:53.000Z
    def joined(self):
        URL = "https://api.scratch.mit.edu/users/" + self.user
        r = requests.get(url = URL)
        data = r.json()
        return data['history']['joined']


    # Get user's profile image URL (string) You can specify a supported size. Ex. https://cdn2.scratch.mit.edu/get_image/user/44834297_90x90.png?v=
    def image(self, size="90x90"):
        URL = "https://api.scratch.mit.edu/users/" + self.user
        r = requests.get(url = URL)
        data = r.json()
        if size == "90x90":
            return data['profile']['images']['90x90']
        elif size == "60x60":
            return data['profile']['images']['60x60']
        elif size == "55x55":
            return data['profile']['images']['55x55']
        elif size == "50x50":
            return data['profile']['images']['50x50']
        elif size == "32x32":
            return data['profile']['images']['32x32']
        else:
            print("\033[1;31;40mBetterScratchAPI Warning: Unsupported image size (" + size + ") given, default size (90x90) was used instead!\033[0;0m")
            return data['profile']['images']['90x90']


    # Get user's status ["What I'm Working On"] (string)
    def status(self):
        URL = "https://api.scratch.mit.edu/users/" + self.user
        r = requests.get(url = URL)
        data = r.json()
        return data['profile']['status']


    # Get user's bio ["About Me"] (string)
    def bio(self):
        URL = "https://api.scratch.mit.edu/users/" + self.user
        r = requests.get(url = URL)
        data = r.json()
        return data['profile']['bio']


    # Get user's country (string) Ex. United States
    def country(self):
        URL = "https://api.scratch.mit.edu/users/" + self.user
        r = requests.get(url = URL)
        data = r.json()
        return data['country']
