import PySimpleGUI as sg
import os
import librosa

from pygame import mixer

from app_threading import thread_with_trace
from audio_search_system import AudioSearchSystem
from display_wav import create_figure, draw_figure

global search_system

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

# sg.SetOptions(background_color='#00706c',      
#            text_element_background_color='#00706c',      
#            element_background_color='#00706c',            
#            input_elements_background_color='#469f9a',
#            button_color=('black','#001b40'),
#            text_color="#ffffff")


# UI elements
image_width = 4
image_height = 2

layout = [[sg.Text('Audio Search System', font=("Helvetica", 20))],      
          [sg.Text('Path to query wav file:', size=(28, 1), font=("Helvetica", 12)), sg.InputText(), sg.FileBrowse()],
          [sg.Text('Folder with wav files to search through:', size=(28, 1), font=("Helvetica", 12)), sg.InputText(), sg.FolderBrowse()],
          [sg.Text('Number of matches to find (per file):', size=(28, 1), font=("Helvetica", 12)), sg.InputText()],
          [sg.Canvas(size=(image_width*100, image_height*100), key='canvas')],
          [sg.ReadButton("Search"), sg.Cancel(), sg.ReadButton("Close Window")],
          [sg.Text('', size=(2, 1))],
          [sg.ProgressBar(1, orientation='h', size=(60, 18), key='progbar')],
          [sg.Text('Matches:', font=("Helvetica", 12))],
          [sg.Text('', size=(50, 18), font=("Helvetica", 14), key='_OUTPUT_')]]

window = sg.Window('Audio Search System').Layout(layout).Finalize() 

# App logic

def run_search():
    print("\nSearching")
    matches = search_system.search()
    matches_result = search_system.print_matches(matches)
    window.FindElement('_OUTPUT_').Update(matches_result)

search_system = None

# defaults
query_wav = "audio/search_testing/query/mozart_query.wav"
db_dir = "audio/search_testing/db"
num_matches = 5

drawn = False

while True:     

    if not drawn:
        print("hi here")
        fig, figure_x, figure_y, figure_w, figure_h = create_figure(librosa.load(query_wav)[0], image_width, image_height)
        fig_photo = draw_figure(window.FindElement('canvas').TKCanvas, fig)
        drawn = True 
    
    event, values = window.Read(timeout=100)

    if search_system:
        window.Element('progbar').UpdateBar(search_system.get_progress())   


    
    if event == "Search":


        # mixer.init()
        # mixer.music.load("audio/search_testing/query/mozart_query.wav")
        # mixer.music.play()


        
        if values[0] != "":  # user input
            query_wav = values[0]
            db_dir = values[1]
            num_matches = int(values[2])
        
        db = []
        for file in os.listdir(db_dir):
            if file.endswith(".wav"):
                db.append(db_dir + "/" + file)
        
        search_system = AudioSearchSystem(query_wav, db, num_matches)

        search_thread = thread_with_trace(target = run_search)
        search_thread.start()
    
    elif event == "Cancel" or event == "Close Window":
        window.Element('progbar').UpdateBar(0)
        if search_system:
            search_system = None
            window.FindElement('_OUTPUT_').Update("")
            search_thread.kill() 
            search_thread.join() 
            if not search_thread.isAlive():
                print("\nCancelled Search")
        # else:
        #     print("\nNo Search happening")
        if event == "Close Window":
            break  

window.Close()
