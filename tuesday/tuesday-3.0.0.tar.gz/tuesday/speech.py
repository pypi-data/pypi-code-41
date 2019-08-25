"""SPEECH module enables your system to speak and listen to your commands very easily
"""
import pyttsx3
import speech_recognition as sr


#giving command to engine
engine=pyttsx3.init('sapi5')
voices=engine.getProperty('voices')
#selecting voice type
engine.setProperty('voice',voices[1].id)
#speak function
def speak(audio):
    """converts string to audio
    """
    
    engine.setProperty('rate', 150)
    engine.say(audio)
    engine.runAndWait()
#take command :takes user audio as input

def takecommand():
    
    r=sr.Recognizer()
    r.energy_threshold=5000
    with sr.Microphone() as source:
        print("listening....")
        r.pause_threshold=1
        audio=r.listen(source)
    try:
        print('recognizing...')
        #language can be manually selected in language variable below
        text=r.recognize_google(audio,language="en-IN")
        print("user said:",text)
    except Exception as e:
        print("can't recognize")
        return "none"
    return text    
def intro():
    
    
    r=sr.Recognizer()
    r.energy_threshold=3000
    with sr.Microphone() as source:
        speak("what is your name")
        
        
        
        print("listening....")
        r.pause_threshold=1
        audio=r.listen(source)
        print('recognizing...')
        try:
            text=r.recognize_google(audio,language="en-IN")
            
            print("user said:",text)
            query=text.replace("my name is","")
            print(query)
            speak(f"hello!{query}, how are you?")
        except:
            speak("can't recognize")    

