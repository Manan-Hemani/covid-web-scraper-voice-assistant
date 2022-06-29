import requests
import json
import pyttsx3
import speech_recognition as sr
import re
import threading
import time

API_KEY = "YOUR API KEY"
PROJECT_TOKEN = "YOUR PROJECT TOKEN"
RUN_TOKEN="YOUR RUN TOKEN" 


class Data:
    def __init__(self , api_key , project_token):
        self.api_key = api_key
        self.project_token = project_token
        self.params = {"api_key": self.api_key}
        self.data = self.GetData()
        
    def GetData(self):
        response = requests.get(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/last_ready_run/data',params=self.params)
        self.data = json.loads(response.text)
        return self.data
        
    def TotalCases(self):
        data = self.data['total']
        
        for content in data:   # loop through the list 
            if content['name'] == "Coronavirus Cases:":
                return content['value']
            
        return "0"
            
    def TotalDeaths(self):
        data = self.data['total']
        
        for content in data:   # loop through the list 
            if content['name'] == "Deaths:":
                return content['value']
            
        return "0"
        
        
    def CountryData(self,country):
        data = self.data['country']
        
        for content in data:   # loop through the list 
            if content['name'].lower() == country.lower():
                return content
            
        return "0"
    
    def CountryList(self):
        countries=[]
        for country in self.data['country']:
            countries.append(country['name'].lower())
            
        return countries
    
    def UpdateData(self):
        response = requests.post(f'https://www.parsehub.com/api/v2/projects/{self.project_token}/run',params=self.params)
        
        def poll():
            time.sleep(0.1)
            old_data = self.data
            while True:
                new_data = self.GetData()
                if new_data != old_data:
                    self.data = new_data
                    print("Data Updated")
                    break
                time.sleep(5)
        t = threading.Thread(target=poll)
        t.start()
        
        

obj = Data(API_KEY,PROJECT_TOKEN)


def speak(text):
    engine=pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    # print(voices[1].id) 
    engine.setProperty('voice',voices[1].id) #can select voices[0] which has a male voice named david
    engine.say(text)
    engine.runAndWait()
    
    
def command():
    r = sr.Recognizer()
    with sr.Microphone() as source:  # use the default microphone as the audio source
        
        r.pause_threshold = 1  # wait time after phrase completion listen
        #r.adjust_for_ambient_noise(source, duration=1)
            
        audio = r.listen(source) # listen for the first phrase and extract it into audio data
         
    try:
        print("Analyzing...")
        text = r.recognize_google(audio)  # can put language as language='en-in' (English - India)
        print("You said ",text)
    
    except Exception as e:
        print("Please say it again...")
        return "None"
    return text  # returns the audio in string
    
    
TOTAL_PATTERNS={
    re.compile("[\w\s]+ total [\w\s]+ cases"):obj.TotalCases,
    re.compile("[\w\s]+ total cases"):obj.TotalCases,
    re.compile("[\w\s]+ total [\w\s]+ deaths"):obj.TotalDeaths,
    re.compile("[\w\s]+ total deaths"):obj.TotalDeaths
}

COUNTRY_PATTERNS = {
    re.compile("[\w\s]+ cases [\w\s]+"): lambda country:obj.CountryData(country)['total_cases'],
    re.compile("[\w\s]+ deaths [\w\s]+"): lambda country:obj.CountryData(country)['total_deaths']
}

UPDATE_DATA_COMMAND = "update"
EXIT_COMMAND = "stop"
countries=obj.CountryList()



if __name__=="__main__":

    while True:
        speak("Listening...")
        print("Listening...")
        query = command()
        result = None

        
        for pattern,func in COUNTRY_PATTERNS.items():
            if pattern.match(query):
                words=query.split(" ")
                for country in countries:
                    if country in words:
                        result = func(country)
                        break
                        
                     
        for pattern,func in TOTAL_PATTERNS.items():
            if pattern.match(query):
                result=func()
                break
        
        if query == UPDATE_DATA_COMMAND:
            result = "Updating Data. This may take some time!"
            obj.UpdateData()
            
        if result:
            speak(result)
            
        if query.find(EXIT_COMMAND) != -1:
            print("Exiting...")
            break