#selenium is a webtool which has different functions to control webbrowser
import webbrowser
from tuesday import speech
import speech_recognition as sr
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time


def google():
    """VOICE SEARCH ON GOOGLE
    """
    speech.speak("what do you want to search?")
    r=sr.Recognizer()
    r.energy_threshold=5000
    with sr.Microphone() as source:
        audio=r.listen(source)
        try:
            text=r.recognize_google(audio,language='en-IN')
            speech.speak("processing")
            url='https://www.google.com/search?q='
            search=url+text
            webbrowser.open(search)
        except:
            speech.speak("can't recognize")
def youtubeplay():
    """PLAY video using your voice
    """
    speech.speak("what do you want to play?")
    r=sr.Recognizer()
    r.energy_threshold=5000
    with sr.Microphone() as source:
        audio=r.listen(source)
        try:
                text=r.recognize_google(audio,language='en-IN')
                speech.speak("processing")
                driver=webdriver.Chrome()
                url="https://www.youtube.com/results?search_query="
                search=url+text
                driver.get(search)
                time.sleep(1)
                play=driver.find_element_by_xpath("//*[@id='video-title']")
                play.click()
                speech.speak("press ENTER to close")
                input('Press ENTER to exit')
        except:
                speech.speak("unable to process your request")         
def youtubesearch():
    speech.speak("what do you want to search?")
    r=sr.Recognizer()
    r.energy_threshold=5000
    with sr.Microphone() as source:
        audio=r.listen(source)
        try:
                text=r.recognize_google(audio,language='en-IN')
                speech.speak("processing")
                driver=webdriver.Chrome()
                url="https://www.youtube.com/results?search_query="
                search=url+text
                driver.get(search)
                speech.speak("press ENTER to close")
                input('Press ENTER to exit') 
        except:
                speech.speak("can't recognize")        

   

        

