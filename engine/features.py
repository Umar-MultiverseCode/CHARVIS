import os
from pipes import quote
import re
import sqlite3
import struct
import subprocess
import time
import webbrowser
from playsound import playsound
import eel
import pyaudio
import pyautogui
import requests
from engine.command import speak
from engine.config import ASSISTANT_NAME
# Playing assiatnt sound function
import pywhatkit as kit
import pvporcupine

from engine.helper import extract_yt_term, remove_words
from hugchat import hugchat

con = sqlite3.connect("jarvis.db")
cursor = con.cursor()

@eel.expose
def playAssistantSound():
    music_dir = "www\\assets\\audio\\start_sound.mp3"
    playsound(music_dir)

def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "")
    query = query.lower().strip()

    # Handle website commands with .com or similar domains
    website_pattern = re.compile(r'^(open|search)\s+(https?://)?([\w\-\.]+\.\w+)(.*)$')
    match = website_pattern.match(query)

    if match:
        protocol = match.group(2) if match.group(2) else 'http://'
        website = match.group(3)
        url = f"{protocol}{website}"

        # Open Google Chrome and navigate to the URL
        try:
            # Open Google Chrome
            subprocess.Popen(["start", "chrome", url], shell=True)
            time.sleep(3)  # Wait for Chrome to open and navigate
            speak(f"Opening {website}")
        except Exception as e:
            speak("Error opening the website")
            print(f"Error: {e}")
        return

    # Existing command handling
    query = query.replace("open", "").strip()

    if query != "":
        try:
            cursor.execute('SELECT path FROM sys_command WHERE name = ?', (query,))
            results = cursor.fetchall()

            if len(results) != 0:
                speak("Opening " + query)
                os.startfile(results[0][0])

            else:
                cursor.execute('SELECT url FROM web_command WHERE name = ?', (query,))
                results = cursor.fetchall()

                if len(results) != 0:
                    speak("Opening " + query)
                    webbrowser.open(results[0][0])

                else:
                    speak("Opening " + query)
                    try:
                        os.system('start ' + query)
                    except:
                        speak("Not found")
        except Exception as e:
            speak("Something went wrong")
            print(e)

       

def PlayYoutube(query):
    search_term = extract_yt_term(query)
    speak("Playing "+search_term+" on YouTube")
    kit.playonyt(search_term)


def hotword():
    porcupine=None
    paud=None
    audio_stream=None
    try:
       
        # pre trained keywords    
        porcupine=pvporcupine.create(keywords=["jarvis","alexa"]) 
        paud=pyaudio.PyAudio()
        audio_stream=paud.open(rate=porcupine.sample_rate,channels=1,format=pyaudio.paInt16,input=True,frames_per_buffer=porcupine.frame_length)
        
        # loop for streaming
        while True:
            keyword=audio_stream.read(porcupine.frame_length)
            keyword=struct.unpack_from("h"*porcupine.frame_length,keyword)

            # processing keyword comes from mic 
            keyword_index=porcupine.process(keyword)

            # checking first keyword detetcted for not
            if keyword_index>=0:
                print("hotword detected")

                # pressing shorcut key win+j
                import pyautogui as autogui
                autogui.keyDown("win")
                autogui.press("j")
                time.sleep(2)
                autogui.keyUp("win")
                
    except:
        if porcupine is not None:
            porcupine.delete()
        if audio_stream is not None:
            audio_stream.close()
        if paud is not None:
            paud.terminate()



# find contacts
def findContact(query):
    
    words_to_remove = [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'wahtsapp', 'video', 'tu']
    query = remove_words(query, words_to_remove)

    try:
        query = query.strip().lower()
        cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
        results = cursor.fetchall()
        print(results[0][0])
        mobile_number_str = str(results[0][0])

        if not mobile_number_str.startswith('+91'):
            mobile_number_str = '+91' + mobile_number_str

        return mobile_number_str, query
    except:
        speak('not exist in contacts')
        return 0, 0
    
def whatsApp(mobile_no, message, flag, name):
    

    if flag == 'message':
        target_tab = 12
        jarvis_message = "message send successfully to "+name

    elif flag == 'call':
        target_tab = 7
        message = ''
        jarvis_message = "calling to "+name

    else:
        target_tab = 6
        message = ''
        jarvis_message = "staring video call with "+name


    # Encode the message for URL
    encoded_message = quote(message)
    print(encoded_message)
    # Construct the URL
    whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={encoded_message}"

    # Construct the full command
    full_command = f'start "" "{whatsapp_url}"'

    # Open WhatsApp with the constructed URL using cmd.exe
    subprocess.run(full_command, shell=True)
    time.sleep(7)
    subprocess.run(full_command, shell=True)
    
    pyautogui.hotkey('ctrl', 'f')

    for i in range(1, target_tab):
        pyautogui.hotkey('tab')

    pyautogui.hotkey('enter')
    speak(jarvis_message)
    
def get_news():
    api_key = "557c58a57feb495aa23c551c96c7d77e"  # Replace with your NewsAPI key
    base_url = f"http://newsapi.org/v2/top-headlines?country=us&apiKey={api_key}"
    response = requests.get(base_url)
    data = response.json()
    
    if data["status"] == "ok":
        articles = data["articles"][:10]  # Get top 10 headlines
        for i, article in enumerate(articles):
            print(f"Headline {i+1}: {article['title']}")
            speak(f"Headline {i+1}: {article['title']}")
            
    else:
        speak("Sorry, I couldn't fetch the news.")
        
        
def get_weather(city):
    api_key = "7e6655d516cc0d5d24f0343a9cc8584b"  # Replace with your OpenWeatherMap API key
    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(base_url)
    data = response.json()
    
    if data["cod"] != "404":
        main = data["main"]
        weather = data["weather"][0]
        temperature = main["temp"]
        description = weather["description"]
        speak(f"The temperature in {city} is {temperature} degrees Celsius with {description}.")
        print(f"The temperature in {city} is {temperature} degrees Celsius with {description}.")
    else:
        speak("City not found.")
        

def searchGoogle(query):
    search_query = query.replace("search", "").strip()
    if search_query:
        # Open Google Chrome if it's not already running
        try:
            # Open a new Chrome window
            subprocess.Popen(["start", "chrome"], shell=True)
            time.sleep(2)  # Wait for Chrome to open
            
            # Type the search query directly into the address bar
            pyautogui.hotkey('ctrl', 'l')  # Focus on the address bar
            pyautogui.typewrite(f"https://www.google.com/search?q={quote(search_query)}")
            pyautogui.press('enter')  # Execute the search
            
            speak(f"Searching for {search_query} on Google")
        except Exception as e:
            speak("Error while searching on Google")
            print(f"Error: {e}")
    else:
        speak("No search query provided")
        
    

# chat bot 
def chatBot(query):
    user_input = query.lower()
    chatbot = hugchat.ChatBot(cookie_path="engine\cookies.json")
    id = chatbot.new_conversation()
    chatbot.change_conversation(id)
    response =  chatbot.chat(user_input)
    print(response)
    speak(response)
    return response

# android automation

def makeCall(name, mobileNo):
    mobileNo =mobileNo.replace(" ", "")
    speak("Calling "+name)
    command = 'adb shell am start -a android.intent.action.CALL -d tel:'+mobileNo
    os.system(command)


# to send message
def sendMessage(message, mobileNo, name):
    from engine.helper import replace_spaces_with_percent_s, goback, keyEvent, tapEvents, adbInput
    message = replace_spaces_with_percent_s(message)
    mobileNo = replace_spaces_with_percent_s(mobileNo)
    speak("sending message")
    goback(4)
    time.sleep(1)
    keyEvent(3)
    # open sms app
    tapEvents(136, 2220)
    #start chat
    tapEvents(819, 2192)
    # search mobile no
    adbInput(mobileNo)
    #tap on name
    tapEvents(601, 574)
    # tap on input
    tapEvents(390, 2270)
    #message
    adbInput(message)
    #send
    tapEvents(957, 1397)
    speak("message send successfully to "+name)
    
    
    

        
