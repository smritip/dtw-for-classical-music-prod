import PySimpleGUI as sg
import os

from audio_search_system import AudioSearchSystem

# Theme Colors
# on Windows, can use sg.ChangeLookAndFeel(...)
# sg.SetOptions(background_color='#d8fffc',      
#            text_element_background_color='#d8fffc',      
#            element_background_color='#d8fffc',            
#            input_elements_background_color='#f4fffe')

# sg.SetOptions(background_color='#11416b',      
#            text_element_background_color='#11416b',      
#            element_background_color='#11416b',            
#            input_elements_background_color='#476c99',
#            button_color=('darkblue','#004441'),
#            text_color="#ffffff")

sg.SetOptions(background_color='#00706c',      
           text_element_background_color='#00706c',      
           element_background_color='#00706c',            
           input_elements_background_color='#469f9a',
           button_color=('black','#001b40'),
           text_color="#ffffff")

# UI elements
layout = [[sg.Text('Audio Search System', font=("Helvetica", 20))],      
          [sg.Text('Path to query wav file:', size=(28, 1), font=("Helvetica", 12)), sg.InputText(), sg.FileBrowse()],
          [sg.Text('Folder with wav files to search through:', size=(28, 1), font=("Helvetica", 12)), sg.InputText(), sg.FolderBrowse()],
          [sg.Text('Number of matches to find (per file):', size=(28, 1), font=("Helvetica", 12)), sg.InputText()],
          [sg.ReadButton("Search"), sg.Cancel(), sg.ReadButton("Close Window")],
          [sg.Text('', size=(2, 1))],
          [sg.Text('Matches:', font=("Helvetica", 12))],
          [sg.Text('', size=(50, 10), font=("Helvetica", 14), key='_OUTPUT_')]]

window = sg.Window('Audio Search System').Layout(layout)  

# Actions
while True:      
    event, values = window.Read()      
    if event == "Search":
        query_wav = values[0]
        db_dir = values[1]
        db = []
        for file in os.listdir(db_dir):
            if file.endswith(".wav"):
                db.append(db_dir + "/" + file)
        num_matches = int(values[2])
        search_system = AudioSearchSystem(query_wav, db, num_matches)
        matches = search_system.search()
        matches_result = search_system.print_matches(matches)
        window.FindElement('_OUTPUT_').Update(matches_result)
    elif event == "Cancel":
        print("Cancelled")
    else:
        break   

window.Close()
