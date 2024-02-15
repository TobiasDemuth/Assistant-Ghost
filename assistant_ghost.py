import speech_recognition as sr
import pyttsx3
import webbrowser
import pyautogui
from googlesearch import search
from datetime import datetime
import os
import csv
import pandas as pd
import subprocess
import tkinter as tk
from tkinter import simpledialog
from translate import Translator
import wikipedia

# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------

key = ""

# commands
search_commands = ["search"]
open_commands = ["open"]
math_commands = ["calculate"]
wdh_commands = ["repeat"]
note_commands = ["note"]
app_commands = ["start"]
trans_commands = ["translate"]
zoom_commands = ["zoom","scale"]
wikipedia_commands = ["wikipedia"]

# dictionarys
trans_dict = {
                "german" : "de",
                "france" : "fr",
                "spain" : "es",
                "italian" : "it",
                "chinese" : "zh",
                "japanese" : "ja",
                "russian" : "ru"
            }

# file names
app_file = "app_paths.txt"

# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------

def speech_to_text(language="en-EN"): # can be changed later also through code
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio, language=language)
        print("you said:", text) # just for debugging
        return text
    except sr.UnknownValueError:
        return None
    except sr.RequestError as e:
        print(f"no result with google API; {e}")
        return None

def text_to_speech(response):
    engine = pyttsx3.init()
    engine.setProperty('rate', 200)  # speaking speach
    engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0') # windows standart voice
    engine.say(response)
    engine.runAndWait()

def offline_translate(text, target_language):
    translator = Translator(to_lang=target_language)
    translation = translator.translate(text)
    return translation

def type_text(text):
    pyautogui.write(text)

def open_first_google_result(query):
    try:
        # get first google-search link
        search_results = search(query, num=1,stop=1)

        # extracting
        first_link = next(search_results, None)

        if first_link:
            webbrowser.open(first_link)
        else:
            print("No link found")
    except Exception as e:
        print(f"Error: {e}")

def get_current_time():
    current_time = datetime.now().strftime("%H:%M:%S")
    current_time = current_time.split(":")
    return f"{current_time[0]} : {current_time[1]}"

def write_note_to_csv(note):
    csv_file = "notes.csv"
    fieldnames = ["Date", "Note"]
    
    if not os.path.exists(csv_file):
        with open(csv_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

    with open(csv_file, 'a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow({"Date": get_current_time(), "Note": note})

def read_notes_from_csv():
    csv_file = "notes.csv"
    fieldnames = ["Date", "Note"]
    
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        return df
    else:
        return "No note found."

def read_notes_with_keyword_from_csv(keyword):
    csv_file = "notes.csv"
    fieldnames = ["Date", "Note"]
    
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)

        matching_notes = df[df['Note'].str.lower().str.contains(keyword.lower())]

        if not matching_notes.empty:
            return f"Notes with keyword '{keyword}':\n" + matching_notes.to_string(index=False)
        else:
            return f"Found no notes with '{keyword}'."
    else:
        return "No notes found."

def delete_notes_with_keyword_from_csv(keyword):
    csv_file = "notes.csv"
    fieldnames = ["Date", "Note"]
    
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)

        matching_notes = df[df['Note'].str.lower().str.contains(keyword.lower())]

        if not matching_notes.empty:
            # reentering not keyword matching notes
            df = df[~df['Note'].str.lower().str.contains(keyword.lower())]
            df.to_csv(csv_file, index=False, encoding='utf-8')
            
            return f"{len(matching_notes)} notes with keyword '{keyword}' were deleted."
        else:
            return f"found no note with the keyword '{keyword}'."
    else:
        return "no note found."

def read_app_paths():
    app_paths = {}

    if os.path.exists(app_file):
        with open(app_file, "r") as file:
            lines = file.readlines()
            for line in lines:
                parts = line.strip().split(",")
                app_paths[parts[0].strip()] = parts[1].strip()
    return app_paths

def write_app_paths(app_paths):
    with open(app_file, "a") as file:
        for app, path in app_paths.items():
            file.write(f"{app},{path}\n")

def add_app_path_gui(app_paths):
    root = tk.Tk()

    app_name = simpledialog.askstring("add app-name", "enter app-name:")
    app_path = simpledialog.askstring("add app-path", "enter app-path:")

    if app_name and app_path:
        app_paths[app_name] = app_path
        write_app_paths(app_paths)
        response = f"app-path for {app_name} were added."
    else:
        response = "error while adding path."

    return response

def zoom_scale(user_input):
    if user_input in ["in","up"]:
        return pyautogui.hotkey('ctrl', '+')
    if user_input in ["out","down"]:
        return pyautogui.hotkey('ctrl', '-')

def get_wikipedia(user_input):
  try:
    result = wikipedia.summary(user_input,1)
    return result
  except:
    return "no wikipage found"
# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------

def personal_assistant():
    last_response = ""
    app_paths = read_app_paths()
    while True:
        user_input = speech_to_text()
        response = ""

        if user_input:
            
            if key in user_input.lower() and any(command in user_input.lower() for command in zoom_commands):
                zoom_query = user_input.lower().replace(key, "").strip()
                zoom_query = " ".join([word if word not in zoom_commands else "" for word in zoom_query.split(" ")]).strip()
                print(zoom_query)
                zoom_scale(zoom_query)
            
            if key in user_input.lower() and any(command in user_input.lower() for command in trans_commands):
                trans_query = user_input.lower().replace(key, "").strip()
                trans_query = " ".join([word if word not in trans_commands else "" for word in trans_query.split(" ")])
                trans_query = trans_query.split(" ")
                input_lang = trans_dict[trans_query[-1].lower()]
                text = str(" ".join(trans_query[0:-2]).strip())
                translation = offline_translate(text,input_lang)
                print(translation)
                response = translation
                
            if key in user_input.lower() and any(command in user_input.lower() for command in wikipedia_commands):
                search_query = user_input.lower().replace(key, "").strip()
                search_query = "".join([word if word not in wikipedia_commands else "" for word in search_query.split(" ")])
                response = get_wikipedia(search_query)

            if key in user_input.lower() and any(command in user_input.lower() for command in app_commands):
                response = user_input.lower()
                app_query = user_input.lower().replace(key, "").strip()
                app_query = "".join([word if word not in app_commands else "" for word in app_query.split(" ")])
                if app_query in app_paths:
                    subprocess.run(str(app_paths[app_query]))
                else:
                    response = f"'{app_query}' was not found. want to add the app?"
                    text_to_speech(response)
                    add_path_response = speech_to_text()
                    if add_path_response and any(word in add_path_response.lower() for word in ["yes", "add"]):
                        response = add_app_path_gui(app_paths)
                    else:
                        response = "ok"
            
            if key in user_input.lower() and any(command in user_input.lower() for command in wdh_commands):
                response = last_response

            if key in user_input.lower() and any(command in user_input.lower() for command in math_commands):
                math_query = user_input.lower().replace(key, "").replace("x", "*").replace(",", ".").strip()
                math_query = "".join([word if word not in math_commands else "" for word in math_query.split(" ")])
                response = eval(math_query)

            if key in user_input.lower() and "time" in user_input.lower():
                response = get_current_time()

            if key in user_input.lower() and "enter text" in user_input.lower():
                response = "ok go on"
                text_to_speech(response)
                input_text = speech_to_text()
                if input_text:
                    type_text(input_text)

            if key in user_input.lower() and any(command in user_input.lower() for command in open_commands):
                open_query = user_input.lower().replace(key, "").strip()
                open_query = "".join([word if word not in open_commands else "" for word in open_query.split(" ")])
                if open_query:
                    response = f"{open_query} is beeing opened."
                    open_first_google_result(open_query)
                else:
                    response = "sorry i didnt understand the request."

            if key in user_input.lower() and any(command in user_input.lower() for command in search_commands):
                search_query = user_input.lower().replace(key, "").strip()
                search_query = "".join([word if word not in search_commands else "" for word in search_query.split(" ")])
                webbrowser.open(f"https://www.google.com/search?q={search_query}")

            if key in user_input.lower() and any(command in user_input.lower() for command in note_commands):
                if "note" in user_input.lower():
                    response = "please enter your note."
                    text_to_speech(response)
                    note_text = speech_to_text()
                    if note_text:
                        write_note_to_csv(note_text)
                        response = "note saved."
                elif "read note" in user_input.lower():
                    notes = read_notes_from_csv()
                    if isinstance(notes, pd.DataFrame):
                        print(notes)
                        response = "notes:\n" + notes.to_string(index=False)
                    else:
                        response = notes
                if key in user_input.lower() and "delete note" in user_input.lower():
                    response = "please enter keyword."
                    text_to_speech(response)
                    keyword = speech_to_text()
                    if keyword:
                        text_to_speech(delete_notes_with_keyword_from_csv(keyword) + ". deleted",)

            elif key in user_input.lower() and "hello" in user_input.lower():
                response = "hello!"

            elif key in user_input.lower() and "goodbye" in user_input.lower():
                text_to_speech("good bye!.")
                with open("conversation.txt", "a") as file:
                    file.write("-----------------------------------------------------------------------------")
                break

            elif key in user_input.lower() and "name" in user_input.lower():
                response = "ghost"

            elif key in user_input.lower() and "thanks" in user_input.lower():
                response = "no problem!"

        text_to_speech(response)
        if response:
            last_response = response
        with open("conversation.txt", "a", encoding="utf-8") as file:
            full_time = datetime.now().strftime("%H:%M:%S")
            if user_input:
                file.write(f"{full_time} \t || \t {user_input} \t => \t {response}\n")
        if datetime.now().strftime("%M") == "00" and datetime.now().strftime("%S") == "00" :
            file.write("-----------------------------------------------------------------------------")



if __name__ == "__main__":
    personal_assistant()
