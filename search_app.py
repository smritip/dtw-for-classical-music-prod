import PySimpleGUI as sg
import os
import librosa

from app_threading import thread_with_trace
from audio_search_system import AudioSearchSystem
from display_wav import create_figure, draw_figure
from constants import *

global search_system, matches_display, matches_index

# UI elements
image_width = 3
image_height = 1.5

## TODO: offset and duration not on for match results

layout = [[sg.Text('')],
          [sg.Text('Audio Search System', font=("Helvetica", 20))],
          [sg.Text('')],      
          [sg.Text('Path to query wav file:', size=(16, 1), font=("Helvetica", 12)), sg.InputText(size=(80, 1), key="__query__"), sg.FileBrowse(initial_folder=os.getcwd())],
          [sg.Text('Start time (mm:ss):', size=(14, 1), font=("Helvetica", 12)), sg.InputText(size=(4, 1), justification='right', key="__start_mins__"), sg.Text(':', size=(1, 1), font=("Helvetica", 12)), sg.InputText(size=(4, 1), justification='right', key="__start_secs__"), sg.Text('', size=(5, 1)),
           sg.Text('End time (mm:ss):', size=(14, 1), font=("Helvetica", 12)), sg.InputText(size=(4, 1), justification='right', key="__end_mins__"), sg.Text(':', size=(1, 1), font=("Helvetica", 12)), sg.InputText(size=(4, 1), justification='right', key="__end_secs__")],
          [sg.Text('Folder with wav files to search through:', size=(28, 1), font=("Helvetica", 12)), sg.InputText(key="__db__"), sg.FolderBrowse(initial_folder=os.getcwd())],
          [sg.Text('Number of matches to find (per file):', size=(28, 1), font=("Helvetica", 12)), sg.InputText(key="__num__")],
          [sg.ReadButton("Search"), sg.Cancel()],
          [sg.ProgressBar(1, orientation='h', size=(30, 15), key='progbar')],
          [sg.Text('', size=(2, 1))],
          [sg.TabGroup([[sg.Tab('Query', [[sg.Text('Select file above', size=(30, 1), font=("Helvetica", 12), key='__query_tab__')]]),
                         sg.Tab('Matches', [[sg.Text('Run search above', size=(30, 1), font=("Helvetica", 12), key='__matches_tab__'), sg.Button("Prev", key="Prev"), sg.ReadButton("Next", key="Next")]])]], key="__tabs__")],
          [sg.Canvas(size=(image_width*100, image_height*100), key='canvas'),
           sg.ReadButton('', image_filename='icons/play_reduced.png', image_size=(30, 30), border_width=0, key='Play'),
           sg.ReadButton('', image_filename='icons/pause_reduced.png', image_size=(30, 30), border_width=0, key='Pause'),
           sg.ReadButton('', image_filename='icons/rewind_reduced.png', image_size=(30, 30), border_width=0, key='Rewind')],
           [sg.Button("Close Window")]]

window = sg.Window('Audio Search System').Layout(layout).Finalize() 

# App logic

search_system = None
matches_display = None
matches_index = 0

def run_search():
    print("\nSearching")
    matches = search_system.search()
    matches_result = search_system.print_matches(matches)
    for match in matches:
        for cut in matches[match]:
            matches_display.append([match, cut[0], cut[1]])
    print(matches_display)

# helper functions

def is_wav(file):
    return file[-4:] == ".wav"

def time_to_secs(mins, secs):
    if mins == '':
        mins = 0
    if secs == '':
        secs = 0
    return (int(mins) * 60) + int(secs)

def get_wav_name(file):
    wav_path_parts = file.split("/")
    return wav_path_parts[-1].split(".")[0]

def draw_wav(wav, vlines=None):
    fig = create_figure(wav, image_width, image_height, vlines)
    fig_photo = draw_figure(window.FindElement('canvas').TKCanvas, fig)
    return fig, fig_photo

# initializations

query_wav = ""
offset = 0.0
duration = None

fig, fig_photo = draw_wav(0)

while True:     

    event, values = window.Read(timeout=100)
  
    # query wav visualization
    if values['__query__'] != query_wav:  # new query wav, so reload wav file
        query_wav = values['__query__']
        window.FindElement('__query_tab__').Update(get_wav_name(query_wav))
        fig, fig_photo = draw_wav(librosa.load(query_wav)[0], vlines=0)
        paused = False  ## TODO: check this      

    # offset and duration
    if query_wav != "":
        start = time_to_secs(values['__start_mins__'], values['__start_secs__'])
        new_offset = start
        end = time_to_secs(values['__end_mins__'], values['__end_secs__'])
        if end == 0:
            new_duration = None
        else:
            new_duration = time_to_secs(values['__end_mins__'], values['__end_secs__']) - new_offset
        if (new_offset != offset) or (new_duration != duration):
            print(new_offset, new_duration)
            offset = new_offset
            duration = new_duration
            fig, fig_photo = draw_wav(librosa.load(query_wav, offset=offset, duration=duration)[0], vlines=0)

    
    # button click events

    if event == "Search":
        
        query_wav = values['__query__']
        db_dir = values['__db__']
        num_matches = int(values['__num__'])

        db = []
        for file in os.listdir(db_dir):
            if file.endswith(".wav"):
                db.append(db_dir + "/" + file)

        query_start = time_to_secs(values['__start_mins__'], values['__start_secs__'])
        query_end = time_to_secs(values['__end_mins__'], values['__end_secs__'])
        
        matches_display = []

        search_system = AudioSearchSystem(query_wav, query_start, query_end, db, num_matches, whole=(query_end == query_start))

        search_thread = thread_with_trace(target = run_search)
        search_thread.start()
    
    elif event == "Cancel" or event == "Close Window" or event is None:
        window.Element('progbar').UpdateBar(0)
        if search_system:
            search_system = None
            search_thread.kill() 
            search_thread.join() 
            if not search_thread.isAlive():
                print("\nCancelled Search")
        if event == "Close Window" or event is None:
            break  

    # progress bar
    if search_system:
        window.Element('progbar').UpdateBar(search_system.get_progress())   


window.Close()
