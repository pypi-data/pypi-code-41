"""Localweather tells the current weather and location with high accuracy
"""

from tuesday import speech
# speech module includes speak function
#imports request module
import requests
#It recognise your speech
import speech_recognition as sr
import geocoder

def weather():
    """Tells current weather
    """    
    api_address='http://api.openweathermap.org/data/2.5/weather?appid=0c42f7f6b53b244c78a418f4f181282a&q='
    speech.speak("name of place sir?")
    r=sr.Recognizer()
    r.energy_threshold=5000
    with sr.Microphone() as source:
        audio=r.listen(source)
        try:
                s=r.recognize_google(audio,language='en-IN')
                print(s)
                speech.speak("processing")
                #using api id geocoder access the weather information
                api_address='http://api.openweathermap.org/data/2.5/weather?appid=0c42f7f6b53b244c78a418f4f181282a&q='
                url = api_address + s
                json_data = requests.get(url).json()
                data=json_data["weather"][0]["description"]
                speech.speak(data)
        except:
                speech.speak("try again")        
def location():#geocoder uses ip address to locate your current location
        """Tells current location
        """
        speech.speak("processing")
        g = geocoder.ip('me')
        a=g.latlng
        b=g.city
        c=g.country
        print(a)
        speech.speak(f"coordinates are {a}")
        print(b)
        speech.speak(f"city is {b}")
        print(c)
        speech.speak(f"and the country is {c}")
        