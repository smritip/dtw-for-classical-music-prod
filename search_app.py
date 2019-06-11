import PySimpleGUI as sg
import os
import librosa
import math

from app_threading import thread_with_trace
from audio_search_system import AudioSearchSystem
from display_wav import create_figure, draw_figure
from constants import *

global search_system, matches_display, matches_index, now_playing, page_index, num_pages

# UI elements
image_width = 3
image_height = 1.5
max_num_matches = 5

## TODO: offset and duration not on for match results
## TODO: resize text
## TODO: enforce max of 50
## TODO: deal with 0 matches?
## TODO: display mm:ss instead of secs in now playing

matches_column = [[sg.Text("\nMatches:")]]

for i in range(max_num_matches):
    matches_column.append([sg.Text("Match", size=(35, 1), key="match"+str(i)), sg.ReadButton("View", key="view"+str(i), disabled=True)])

matches_column.append([sg.Button("Prev", key="Prev"), sg.ReadButton("Next", key="Next"), sg.Text("", key="__matches_fraction__")])

media_player = [[sg.Canvas(size=(image_width*100, image_height*100), key='canvas'),
                 sg.ReadButton('', image_filename='icons/play_reduced.png', image_size=(30, 30), border_width=0, key='Play'),
                 sg.ReadButton('', image_filename='icons/pause_reduced.png', image_size=(30, 30), border_width=0, key='Pause'),
                 sg.ReadButton('', image_filename='icons/rewind_reduced.png', image_size=(30, 30), border_width=0, key='Rewind')],
                 [sg.Text('Now Playing:', size=(50, 1), key="__now_playing__")]]

layout = [[sg.Text('')],
          [sg.Text('Audio Search System', font=("Helvetica", 20))],
          [sg.Text('')],      
          [sg.Text('Path to query wav file:', size=(16, 1), font=("Helvetica", 12)), sg.InputText(size=(80, 1), key="__query__"), sg.FileBrowse(initial_folder=os.getcwd()), sg.ReadButton("View Query", key="View Query")],
          [sg.Text('Start time (mm:ss):', size=(14, 1), font=("Helvetica", 12)), sg.InputText(size=(4, 1), justification='right', key="__start_mins__"), sg.Text(':', size=(1, 1), font=("Helvetica", 12)), sg.InputText(size=(4, 1), justification='right', key="__start_secs__"), sg.Text('', size=(5, 1)),
           sg.Text('End time (mm:ss):', size=(14, 1), font=("Helvetica", 12)), sg.InputText(size=(4, 1), justification='right', key="__end_mins__"), sg.Text(':', size=(1, 1), font=("Helvetica", 12)), sg.InputText(size=(4, 1), justification='right', key="__end_secs__")],
          [sg.Text('Folder with wav files to search through:', size=(28, 1), font=("Helvetica", 12)), sg.InputText(key="__db__"), sg.FolderBrowse(initial_folder=os.getcwd())],
          [sg.Text('Number of matches to find (per file):', size=(28, 1), font=("Helvetica", 12)), sg.InputText(key="__num__")],
          [sg.ReadButton("Search"), sg.Cancel()],
          [sg.ProgressBar(1, orientation='h', size=(30, 15), key='progbar')],
          [sg.Text('', size=(2, 1))],
          [sg.Column(matches_column), sg.Column(media_player)],
          # [sg.TabGroup([[sg.Tab('Query', [[sg.Text('Select file above', size=(30, 1), font=("Helvetica", 12), key='__query_tab__')]]),
          #                sg.Tab('Matches', [[sg.Text('Run search above', size=(30, 1), font=("Helvetica", 12), key='__matches_tab__'), sg.Button("Prev", key="Prev"), sg.ReadButton("Next", key="Next")]])]], key="__tabs__"), sg.Column(media_player)],
           [sg.Button("Close Window")]]


window = sg.Window('Audio Search System').Layout(layout).Finalize() 

# for i in range(max_num_matches):
#     window.FindElement('view'+str(i)).Update(visible=False)

# App logic

search_system = None
matches_display = None
matches_index = 0
now_playing = None
page_index = 0
num_pages = 1

def run_search():
    print("\nSearching")
    matches = search_system.search()
    matches_result = search_system.print_matches(matches)
    
    for match in matches:
        for cut in matches[match]:
            matches_display.append([match, cut[0], cut[1]])
    print(matches_display)
    matches_index = 0
    # num_pages = math.ceil(len(matches_display) / max_num_matches)
    # print("changing", num_pages)

# helper functions
# 46.625668934240366, 52.94149659863945

def is_wav(file):
    return file[-4:] == ".wav"

def time_to_secs(mins, secs):
    if mins == '':
        mins = 0
    if secs == '':
        secs = 0
    return (float(mins) * 60) + float(secs)

def secs_to_mins(secs):
    secs = int(secs)
    return int(secs/60), secs % 60

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

    # query wav visualization (and user input checks)
    if is_wav(values['__query__']):
        window.Element('View Query').Update(disabled=False)
        if values['__query__'] != query_wav:  # new query wav, so reload wav file
            query_wav = values['__query__']
            fig, fig_photo = draw_wav(librosa.load(query_wav)[0], vlines=0)
            window.Element('__now_playing__').Update("Now Playing: " + get_wav_name(query_wav) + ": 0.00 - 0.00")
            now_playing = query_wav
            paused = False  ## TODO: check this
    else:
        window.Element('View Query').Update(disabled=True)

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
            start = ("{:0.2f}").format(offset)
            end = ("{:0.2f}").format(offset + duration) if (duration is not None) else ''
            display_text = get_wav_name(query_wav) + ": " + start + " - " + end
            window.Element('__now_playing__').Update("Now Playing: " + display_text)
            now_playing = query_wav

    if matches_display:

        # TODO: optimize so not happening all the time, just on new pages
        # print(min(len(matches_display), max_num_matches))
        num_pages = math.ceil(len(matches_display) / max_num_matches)

        start_num_results = str((page_index * max_num_matches) + 1)
        if len(matches_display) > max_num_matches:
            end_num_results = str(min((len(matches_display) + 1) - int(start_num_results), max_num_matches) + int(start_num_results) - 1)
        else:
            end_num_results = str(len(matches_display))
        window.Element('__matches_fraction__').Update(start_num_results + " - " + end_num_results + " of " + str(len(matches_display)))

        start_match_index = page_index * max_num_matches
        for i in range(max_num_matches):
            index = start_match_index + i
            if index >= len(matches_display):
                window.Element("match"+str(i)).Update("Match")
                window.Element("view"+str(i)).Update(disabled=True)
            else:
                display_text = get_wav_name(matches_display[index][0]) + ": " + ("{:0.2f}").format(matches_display[index][1]) + " - " + ("{:0.2f}").format(matches_display[index][2])
                window.Element("match"+str(i)).Update(display_text)
                window.Element("view"+str(i)).Update(disabled=False)

        
        
        # current_match = matches_display[matches_index]
        # current_wav = current_match[0]
        # if current_wav != now_playing:
        #     print("updating with index", matches_index)
        #     current_offset = float(current_match[1])
        #     current_duration = float(current_match[2] - current_match[1])
        #     fig, fig_photo = draw_wav(librosa.load(current_wav, offset=current_offset, duration=current_duration)[0], vlines=0)
        #     now_playing = current_wav

    
    # button click events
    if event == "view0":
        match_index = page_index * max_num_matches
        print(match_index)
        current_match = matches_display[match_index]
        current_wav = current_match[0]
        print("updating with index", match_index)
        current_offset = float(current_match[1])
        current_duration = float(current_match[2] - current_match[1])
        fig, fig_photo = draw_wav(librosa.load(current_wav, offset=current_offset, duration=current_duration)[0], vlines=0)
        display_text = get_wav_name(current_wav) + ": " + ("{:0.2f}").format(current_offset) + " - " + ("{:0.2f}").format(current_offset + current_duration)
        window.Element('__now_playing__').Update("Now Playing: " + display_text)
        now_playing = current_wav

        # display_text = get_wav_name(query_wav) + ": " + start + " - " + end
        #     window.Element('__now_playing__').Update("Now Playing: " + display_text)
        #     now_playing = query_wav

    if event == "view1":
        match_index = (page_index * max_num_matches) + 1
        print(match_index)
        current_match = matches_display[match_index]
        current_wav = current_match[0]
        print("updating with index", match_index)
        current_offset = float(current_match[1])
        current_duration = float(current_match[2] - current_match[1])
        fig, fig_photo = draw_wav(librosa.load(current_wav, offset=current_offset, duration=current_duration)[0], vlines=0)
        display_text = get_wav_name(current_wav) + ": " + ("{:0.2f}").format(current_offset) + " - " + ("{:0.2f}").format(current_offset + current_duration)
        window.Element('__now_playing__').Update("Now Playing: " + display_text)
        now_playing = current_wav

    if event == "view2":
        match_index = (page_index * max_num_matches) + 2
        print(match_index)
        current_match = matches_display[match_index]
        current_wav = current_match[0]
        print("updating with index", match_index)
        current_offset = float(current_match[1])
        current_duration = float(current_match[2] - current_match[1])
        fig, fig_photo = draw_wav(librosa.load(current_wav, offset=current_offset, duration=current_duration)[0], vlines=0)
        display_text = get_wav_name(current_wav) + ": " + ("{:0.2f}").format(current_offset) + " - " + ("{:0.2f}").format(current_offset + current_duration)
        window.Element('__now_playing__').Update("Now Playing: " + display_text)
        now_playing = current_wav

    if event == "view3":
        match_index = (page_index * max_num_matches) + 3
        print(match_index)
        current_match = matches_display[match_index]
        current_wav = current_match[0]
        print("updating with index", match_index)
        current_offset = float(current_match[1])
        current_duration = float(current_match[2] - current_match[1])
        fig, fig_photo = draw_wav(librosa.load(current_wav, offset=current_offset, duration=current_duration)[0], vlines=0)
        display_text = get_wav_name(current_wav) + ": " + ("{:0.2f}").format(current_offset) + " - " + ("{:0.2f}").format(current_offset + current_duration)
        window.Element('__now_playing__').Update("Now Playing: " + display_text)
        now_playing = current_wav

    if event == "view4":
        match_index = (page_index * max_num_matches) + 4
        print(match_index)
        current_match = matches_display[match_index]
        current_wav = current_match[0]
        print("updating with index", match_index)
        current_offset = float(current_match[1])
        current_duration = float(current_match[2] - current_match[1])
        fig, fig_photo = draw_wav(librosa.load(current_wav, offset=current_offset, duration=current_duration)[0], vlines=0)
        display_text = get_wav_name(current_wav) + ": " + ("{:0.2f}").format(current_offset) + " - " + ("{:0.2f}").format(current_offset + current_duration)
        window.Element('__now_playing__').Update("Now Playing: " + display_text)
        now_playing = current_wav

    if page_index == 0:
        window.Element('Prev').Update(disabled=True)
    else:
        window.Element('Prev').Update(disabled=False)

    if page_index == (num_pages - 1):
        window.Element('Next').Update(disabled=True)
    else: 
        window.Element('Next').Update(disabled=False)

    if event == "Next":
        page_index += 1
        print("page i", page_index)
        # start_num_results = (page_index * max_num_matches) + 1
        # end_num_results = min((len(matches_display) + 1) - max_num_matches, max_num_matches) + start_num_results
        # # window.Element('__matches_fraction__').Update(start_num_results + " - " + end_num_results + " of " + len(matches_display))
        start_num_results = str((page_index * max_num_matches) + 1)
        if len(matches_display) > max_num_matches:
            end_num_results = str(min((len(matches_display) + 1) - max_num_matches, max_num_matches) + int(start_num_results) - 1)
        else:
            end_num_results = str(len(matches_display))
        window.Element('__matches_fraction__').Update(start_num_results + " - " + end_num_results + " of " + str(len(matches_display)))

    if event == "Prev":
        page_index -= 1
        start_num_results = str((page_index * max_num_matches) + 1)
        if len(matches_display) > max_num_matches:
            end_num_results = str(min((len(matches_display) + 1) - max_num_matches, max_num_matches) + int(start_num_results) - 1)
        else:
            end_num_results = str(len(matches_display))
        window.Element('__matches_fraction__').Update(start_num_results + " - " + end_num_results + " of " + str(len(matches_display)))

    if event == "View Query":
        query_wav = values['__query__'] 
        fig, fig_photo = draw_wav(librosa.load(query_wav)[0], vlines=0) 
        window.Element('__now_playing__').Update("Now Playing: " + get_wav_name(query_wav) + ": 0.00 - 0.00")
        now_playing = query_wav
        paused = False  ## TODO: check this 

    if event == "Next":
        matches_index += 1
        if matches_index == len(matches_display):
            matches_index = 0

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
