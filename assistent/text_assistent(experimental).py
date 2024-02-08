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

key = ""
search_commands = ["suche", "suchen", "such", "search"]
open_commands = ["öffne", "öffnen", "open"]
math_commands = ["berechne"]
wdh_commands = ["wiederhole", "nochmal", "wie bitte"]
note_commands = ["notizen", "notiere", "schreibe auf"]
app_commands = ["starte"]
trans_commands = ["übersetze"]

app_file = "app_paths.txt"

def text_to_speech(response):
    engine = pyttsx3.init()
    engine.setProperty('rate', 200)  # Ändern Sie die Sprechgeschwindigkeit nach Bedarf
    engine.say(response)
    engine.runAndWait()

def offline_translate(text, target_language):
    translator= Translator(from_lang= "de",to_lang=target_language)
    translation = translator.translate(text)
    return translation

def type_text(text):
    pyautogui.write(text)

def open_first_google_result(query):
    try:
        # Verwenden Sie die googlesearch-python-Bibliothek, um die ersten Suchergebnisse zu erhalten
        search_results = search(query, num_results=1)

        # Extrahieren Sie den ersten Link aus den Suchergebnissen
        first_link = next(search_results, None)

        if first_link:
            webbrowser.open(first_link)
        else:
            print("Kein geeigneter Link im ersten Suchergebnis gefunden.")
    except Exception as e:
        print(f"Fehler beim Abrufen der Suchergebnisse: {e}")

def get_current_time():
    current_time = datetime.now().strftime("%H:%M:%S")
    current_time = current_time.split(":")
    return f"{current_time[0]} Uhr {current_time[1]}"

def write_note_to_csv(note):
    csv_file = "notizen.csv"
    fieldnames = ["Zeitpunkt", "Notiz"]
    
    if not os.path.exists(csv_file):
        with open(csv_file, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

    with open(csv_file, 'a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow({"Zeitpunkt": get_current_time(), "Notiz": note})

def read_notes_from_csv():
    csv_file = "notizen.csv"
    fieldnames = ["Zeitpunkt", "Notiz"]
    
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        return df
    else:
        return "Keine Notizen gefunden."

def read_notes_with_keyword_from_csv(keyword):
    csv_file = "notizen.csv"
    fieldnames = ["Zeitpunkt", "Notiz"]
    
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)

        matching_notes = df[df['Notiz'].str.lower().str.contains(keyword.lower())]

        if not matching_notes.empty:
            return f"Notizen mit dem Schlüsselwort '{keyword}':\n" + matching_notes.to_string(index=False)
        else:
            return f"Keine Notizen mit dem Schlüsselwort '{keyword}' gefunden."
    else:
        return "Keine Notizen gefunden."

def delete_notes_with_keyword_from_csv(keyword):
    csv_file = "notizen.csv"
    fieldnames = ["Zeitpunkt", "Notiz"]
    
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)

        matching_notes = df[df['Notiz'].str.lower().str.contains(keyword.lower())]

        if not matching_notes.empty:
            # Schreibe die verbleibenden Notizen (ohne die mit dem Schlüsselwort) zurück in die Datei
            df = df[~df['Notiz'].str.lower().str.contains(keyword.lower())]
            df.to_csv(csv_file, index=False, encoding='utf-8')
            
            return f"{len(matching_notes)} Notizen mit dem Schlüsselwort '{keyword}' wurden gelöscht."
        else:
            return f"Keine Notizen mit dem Schlüsselwort '{keyword}' gefunden."
    else:
        return "Keine Notizen gefunden."

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

    app_name = simpledialog.askstring("App-Pfad hinzufügen", "Namen der App eingeben:")
    app_path = simpledialog.askstring("App-Pfad hinzufügen", "Pfad zur App eingeben:")

    if app_name and app_path:
        app_paths[app_name] = app_path
        write_app_paths(app_paths)
        response = f"App-Pfad für {app_name} wurde hinzugefügt."
    else:
        response = "Fehler beim Hinzufügen des App-Pfads."

    return response

def personal_assistant(user_input):
    last_response = ""
    app_paths = read_app_paths()
    user_input = user_input
    response = ""
    if user_input:
        
        if key in user_input.lower() and any(command in user_input.lower() for command in trans_commands):
            trans_query = user_input.lower().replace(key, "").strip()
            trans_query = " ".join([word if word not in trans_commands else "" for word in trans_query.split(" ")])
            print(offline_translate(trans_query,"en"))
            response = offline_translate(trans_query,"en")
        
        if key in user_input.lower() and any(command in user_input.lower() for command in app_commands):
            response = user_input.lower()
            app_query = user_input.lower().replace(key, "").strip()
            app_query = "".join([word if word not in app_commands else "" for word in app_query.split(" ")])
            if app_query in app_paths:
                subprocess.run(str(app_paths[app_query]))
            else:
                response = f"Die App '{app_query}' wurde nicht gefunden. Möchten Sie den Pfad hinzufügen?"
                text_to_speech(response)
                add_path_response = user_input
                if add_path_response and any(word in add_path_response.lower() for word in ["ja", "hinzufügen"]):
                    response = add_app_path_gui(app_paths)
        
        if key in user_input.lower() and any(command in user_input.lower() for command in wdh_commands):
            response = last_response
        if key in user_input.lower() and any(command in user_input.lower() for command in math_commands):
            math_query = user_input.lower().replace(key, "").replace("x", "*").replace(",", ".").strip()
            math_query = "".join([word if word not in math_commands else "" for word in math_query.split(" ")])
            response = eval(math_query)
        if key in user_input.lower() and "wie spät" in user_input.lower():
            response = get_current_time()
        if key in user_input.lower() and "gebe ein" in user_input.lower():
            response = "Eingabetext sagen"
            text_to_speech(response)
            input_text = user_input
            if input_text:
                type_text(input_text)
        if key in user_input.lower() and any(command in user_input.lower() for command in open_commands):
            open_query = user_input.lower().replace(key, "").replace("nach", "").strip()
            open_query = "".join([word if word not in open_commands else "" for word in open_query.split(" ")])
            if open_query:
                response = f"Ich öffne {open_query} für Sie."
                open_first_google_result(open_query)
            else:
                response = "Entschuldigung, ich habe keine Suchanfrage verstanden."
        if key in user_input.lower() and any(command in user_input.lower() for command in search_commands):
            search_query = user_input.lower().replace(key, "").strip()
            search_query = "".join([word if word not in search_commands else "" for word in search_query.split(" ")])
            webbrowser.open(f"https://www.google.com/search?q={search_query}")
        if key in user_input.lower() and any(command in user_input.lower() for command in note_commands):
            if "notiere" in user_input.lower() or "schreibe auf" in user_input.lower():
                response = "Bitte sagen Sie die Notiz, die Sie speichern möchten."
                text_to_speech(response)
                note_text = user_input
                if note_text:
                    write_note_to_csv(note_text)
                    response = "Notiz wurde gespeichert."
            elif "lies notizen" in user_input.lower():
                notes = read_notes_from_csv()
                if isinstance(notes, pd.DataFrame):
                    print(notes)
                    response = "Hier sind Ihre Notizen:\n" + notes.to_string(index=False)
                else:
                    response = notes
            if key in user_input.lower() and "lösche notizen" in user_input.lower():
                response = "Welche Notizen möchten Sie löschen? Sagen Sie das Schlüsselwort."
                text_to_speech(response)
                keyword = user_input
                if keyword:
                    text_to_speech(
                        delete_notes_with_keyword_from_csv(keyword) + ".  wirklich löschen?",
                    )
        elif key in user_input.lower() and "hallo" in user_input.lower():
            response = "Hallo!"
        elif key in user_input.lower() and "auf wiedersehen" in user_input.lower():
            text_to_speech("Auf Wiedersehen! Haben Sie einen schönen Tag.")
            with open("gespräch.txt", "a") as file:
                file.write("-----------------------------------------------------------------------------")
        elif key in user_input.lower() and "name" in user_input.lower():
            response = "geheim"
        elif key in user_input.lower() and "danke" in user_input.lower():
            response = "Gern geschehen!"
    
    if response:
        last_response = response
    with open("gespräch.txt", "a") as file:
        full_time = datetime.now().strftime("%H:%M:%S")
        if user_input:
            file.write(f"{full_time} \t || \t {user_input} \t => \t {response}\n")
    if datetime.now().strftime("%M") == "00" and datetime.now().strftime("%S") == "00" :
        file.write("-----------------------------------------------------------------------------")
    return response

class PersonalAssistantGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Personal Assistant")

        self.create_widgets()

    def create_widgets(self):
        self.user_input_label = tk.Label(self.root, text="Benutzereingabe:")
        self.user_input_label.pack()

        self.user_input_text = tk.Text(self.root, height=5, width=40)
        self.user_input_text.pack()

        self.process_button = tk.Button(self.root, text="Verarbeiten", command=self.process_user_input)
        self.process_button.pack()

        self.response_label = tk.Label(self.root, text="Antwort:")
        self.response_label.pack()

        self.response_text = tk.Text(self.root, height=5, width=40)
        self.response_text.pack()

    def process_user_input(self):
        user_input = self.user_input_text.get("1.0", tk.END).strip()
        response = personal_assistant(user_input)
        self.user_input_text.delete(1.0, tk.END)
        self.response_text.delete(1.0, tk.END)  # Löscht vorherige Antwort
        self.response_text.insert(tk.END, response)
        text_to_speech(response)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    gui = PersonalAssistantGUI()
    gui.run()