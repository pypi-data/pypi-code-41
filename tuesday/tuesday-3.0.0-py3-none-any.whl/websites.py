#Voice controlled search
#Only DOMAIN SUFFIX is required
from tuesday import speech
#Webbrowser module provides accessibility to browser
import webbrowser
import speech_recognition as sr
import pyttsx3

def Open(SUFFIX):
    '''input is .com,.net,.in .....etc'''
    try:
        r=sr.Recognizer()
        r.energy_threshold=5000
        with sr.Microphone() as source:
            speech.speak("name of the site")
            audio=r.listen(source)
            print('recognizing...')
            text=r.recognize_google(audio,language='en-IN')
            print("user said:",text)
        search=text+SUFFIX
        #Open required site     
        webbrowser.open(search)
    except:
        speech.speak("try again")    
