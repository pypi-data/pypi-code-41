#wikipedia module contains several functions
import wikipedia
import pyttsx3
import speech_recognition as sr



#giving command to engine
engine=pyttsx3.init('sapi5')
voices=engine.getProperty('voices')
#speak function
def speak(audio):
        engine.setProperty('rate', 150)
        engine.say(audio)
        engine.runAndWait()
#take command :takes user audio as input
def text(query):
        """Search wikipedia by user text input
        """
        results=wikipedia.summary(query,sentences=3)#you can get more than 3 sentences in result
        print(results)
def voice():
        """VOICE search wikipedia
        """
        r=sr.Recognizer()
        r.energy_threshold=3000
        with sr.Microphone() as source:
                print("listening....")
                r.pause_threshold=1
                audio=r.listen(source)
                try:
                        text=r.recognize_google(audio,language='en-IN')
                        print("user said:",text)
                        results=wikipedia.summary(text,sentences=3)#you can get more than 3 sentences in result
                        print(results)
                        speak(results)
                except:
                        speak("try again")        


