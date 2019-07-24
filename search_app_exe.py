import PySimpleGUI as sg
import os
import librosa
import math
# import tempfile

# import time

# from pygame import mixer

# from pydub import AudioSegment

from app_threading import thread_with_trace
from audio_search_system_exe import AudioSearchSystem
# from display_wav import create_figure, draw_figure
from constants import *

global search_system, matches_display, matches_index, now_playing, page_index, num_pages, current_matches_display, media_start_time, media_end_time, paused, rewind, mp3_fd, now_playing_mp3_path

# UI elements
image_width = 3
image_height = 1.5
max_num_matches = 5

mp3_fd = None
now_playing_mp3_path = None

## TODO: auto-resize text to fit
## TODO: deal with 0 matches?
## TODO: display mm:ss instead of secs in now playing
## TODO: move back playhead

matches_column = [[sg.Text("\nMatches:")]]

for i in range(max_num_matches):
    matches_column.append([sg.Text("--", size=(35, 1), key="match"+str(i)), sg.ReadButton("View", key="view"+str(i), disabled=True)])

matches_column.append([sg.Button("Prev", key="Prev"), sg.ReadButton("Next", key="Next"), sg.Text("", size=(30, 1), key="__matches_fraction__")])

media_player = [[sg.Canvas(size=(image_width*100, image_height*100), key='canvas'),
                 sg.ReadButton('', image_filename='icons/play_reduced.png', image_size=(30, 30), border_width=0, key='Play'),
                 sg.ReadButton('', image_filename='icons/pause_reduced.png', image_size=(30, 30), border_width=0, key='Pause'),
                 sg.ReadButton('', image_filename='icons/rewind_reduced.png', image_size=(30, 30), border_width=0, key='Rewind')],
                 [sg.Text('Now Playing:', size=(70, 1), key="__now_playing__")]]

layout = [[sg.Text('')],
          [sg.Text('Audio Search System', font=("Helvetica", 20))],
          [sg.Text('')],      
          [sg.Text('Path to query wav file:', size=(16, 1), font=("Helvetica", 12)), sg.InputText(size=(80, 1), key="__query__"), sg.FileBrowse(initial_folder=os.getcwd())],
          [sg.Text('Start time (mm:ss):', size=(14, 1), font=("Helvetica", 12)), sg.InputText(size=(4, 1), justification='right', key="__start_mins__"), sg.Text(':', size=(1, 1), font=("Helvetica", 12)), sg.InputText(size=(4, 1), justification='right', key="__start_secs__"), sg.Text('', size=(5, 1)),
           sg.Text('End time (mm:ss):', size=(14, 1), font=("Helvetica", 12)), sg.InputText(size=(4, 1), justification='right', key="__end_mins__"), sg.Text(':', size=(1, 1), font=("Helvetica", 12)), sg.InputText(size=(4, 1), justification='right', key="__end_secs__"), sg.Text('', size=(18, 1)),
           sg.ReadButton("View Query", key="View Query")],
          [sg.Text('Folder with wav files to search through:', size=(28, 1), font=("Helvetica", 12)), sg.InputText(key="__db__"), sg.FolderBrowse(initial_folder=os.getcwd())],
          [sg.Text('Number of matches to find (per file):', size=(28, 1), font=("Helvetica", 12)), sg.InputText(key="__num__")],
          [sg.ReadButton("Search", key="Search"), sg.Cancel()],
          [sg.ProgressBar(1, orientation='h', size=(30, 15), key='progbar')],
          [sg.Text('', size=(2, 1))],
          [sg.Column(matches_column), sg.Column(media_player)],
          [sg.Text('', size=(2, 1))],
          [sg.Button("Close Window")],
          [sg.Text('', size=(2, 1))]]


window = sg.Window('Audio Search System').Layout(layout).Finalize() 


# App logic

search_system = None
matches_display = None
matches_index = 0
now_playing = None
page_index = 0
num_pages = 1
current_matches_display = None

# mixer.init()
media_start_time = None
media_end_time = None
paused = False
rewind = False

def run_search():
    print("\nSearching")
    matches = search_system.search()
    matches_result = search_system.print_matches(matches)
    
    for match in matches:
        for cut in matches[match]:
            matches_display.append([match, cut[0], cut[1]])
    print(matches_display)
    current_matches_display = matches_display
    matches_index = 0

# helper functions

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

# def draw_wav(wav, vlines=None):
#     fig = create_figure(wav, image_width, image_height, vlines)
#     fig_photo = draw_figure(window.FindElement('canvas').TKCanvas, fig)
#     return fig, fig_photo

# initializations

query_wav = ""
offset = 0.0
duration = None
query_offset = 0.0  ## todo: clean this up
query_duration = 0.0

# fig, fig_photo = draw_wav(0)

while True:     

    event, values = window.Read(timeout=100)

    # TODO: user input checks (valid wav file, valid folder, valid number of matches)
    # TODO: default of number of matches?

    # query wav visualization (and user input checks)
    if is_wav(values['__query__']):
        window.Element('View Query').Update(disabled=False)
    else:
        window.Element('View Query').Update(disabled=True)


    if matches_display:

        if matches_display != current_matches_display:
            current_matches_display = matches_display
            page_index = 0
            for i in range(max_num_matches):
                window.Element("match"+str(i)).Update("--")
                window.Element("view"+str(i)).Update(disabled=True)

        # TODO: optimize so not happening all the time, just on new pages
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
                window.Element("match"+str(i)).Update("--")
                window.Element("view"+str(i)).Update(disabled=True)
            else:
                display_text = get_wav_name(matches_display[index][0]) + ": " + ("{:0.2f}").format(matches_display[index][1]) + " - " + ("{:0.2f}").format(matches_display[index][2])
                window.Element("match"+str(i)).Update(display_text)
                window.Element("view"+str(i)).Update(disabled=False)

    
    # button click events
    # if event == "view0":
    #     match_index = page_index * max_num_matches
    #     print(match_index)
    #     current_match = matches_display[match_index]
    #     current_wav = current_match[0]
    #     print("updating with index", match_index)
    #     current_offset = float(current_match[1])
    #     current_duration = float(current_match[2] - current_match[1])
    #     fig, fig_photo = draw_wav(librosa.load(current_wav, offset=current_offset, duration=current_duration)[0], vlines=0.01)
    #     display_text = get_wav_name(current_wav) + ": " + ("{:0.2f}").format(current_offset) + " - " + ("{:0.2f}").format(current_offset + current_duration)
    #     window.Element('__now_playing__').Update("Now Playing: " + display_text + "  seconds")
    #     now_playing = current_wav
    #     paused = False
    #     offset = current_offset
    #     duration = current_duration


    # if event == "view1":
    #     match_index = (page_index * max_num_matches) + 1
    #     print(match_index)
    #     current_match = matches_display[match_index]
    #     current_wav = current_match[0]
    #     print("updating with index", match_index)
    #     current_offset = float(current_match[1])
    #     current_duration = float(current_match[2] - current_match[1])
    #     fig, fig_photo = draw_wav(librosa.load(current_wav, offset=current_offset, duration=current_duration)[0], vlines=0.01)
    #     display_text = get_wav_name(current_wav) + ": " + ("{:0.2f}").format(current_offset) + " - " + ("{:0.2f}").format(current_offset + current_duration)
    #     window.Element('__now_playing__').Update("Now Playing: " + display_text + "  seconds")
    #     now_playing = current_wav
    #     paused = False
    #     offset = current_offset
    #     duration = current_duration

    # if event == "view2":
    #     match_index = (page_index * max_num_matches) + 2
    #     print(match_index)
    #     current_match = matches_display[match_index]
    #     current_wav = current_match[0]
    #     print("updating with index", match_index)
    #     current_offset = float(current_match[1])
    #     current_duration = float(current_match[2] - current_match[1])
    #     fig, fig_photo = draw_wav(librosa.load(current_wav, offset=current_offset, duration=current_duration)[0], vlines=0.01)
    #     display_text = get_wav_name(current_wav) + ": " + ("{:0.2f}").format(current_offset) + " - " + ("{:0.2f}").format(current_offset + current_duration)
    #     window.Element('__now_playing__').Update("Now Playing: " + display_text + "  seconds")
    #     now_playing = current_wav
    #     paused = False
    #     offset = current_offset
    #     duration = current_duration

    # if event == "view3":
    #     match_index = (page_index * max_num_matches) + 3
    #     print(match_index)
    #     current_match = matches_display[match_index]
    #     current_wav = current_match[0]
    #     print("updating with index", match_index)
    #     current_offset = float(current_match[1])
    #     current_duration = float(current_match[2] - current_match[1])
    #     fig, fig_photo = draw_wav(librosa.load(current_wav, offset=current_offset, duration=current_duration)[0], vlines=0.01)
    #     display_text = get_wav_name(current_wav) + ": " + ("{:0.2f}").format(current_offset) + " - " + ("{:0.2f}").format(current_offset + current_duration)
    #     window.Element('__now_playing__').Update("Now Playing: " + display_text + "  seconds")
    #     now_playing = current_wav
    #     paused = False
    #     offset = current_offset
    #     duration = current_duration

    # if event == "view4":
    #     match_index = (page_index * max_num_matches) + 4
    #     print(match_index)
    #     current_match = matches_display[match_index]
    #     current_wav = current_match[0]
    #     print("updating with index", match_index)
    #     current_offset = float(current_match[1])
    #     current_duration = float(current_match[2] - current_match[1])
    #     fig, fig_photo = draw_wav(librosa.load(current_wav, offset=current_offset, duration=current_duration)[0], vlines=0.01)
    #     display_text = get_wav_name(current_wav) + ": " + ("{:0.2f}").format(current_offset) + " - " + ("{:0.2f}").format(current_offset + current_duration)
    #     window.Element('__now_playing__').Update("Now Playing: " + display_text + "  seconds")
    #     now_playing = current_wav
    #     paused = False
    #     offset = current_offset
    #     duration = current_duration

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

    # if event == "View Query":
    #     print("hi, hello")
    #     query_wav = values['__query__']
    #     start = time_to_secs(values['__start_mins__'], values['__start_secs__'])
    #     new_offset = start
    #     end = time_to_secs(values['__end_mins__'], values['__end_secs__'])
    #     if end == 0:
    #         new_duration = None
    #     else:
    #         new_duration = time_to_secs(values['__end_mins__'], values['__end_secs__']) - new_offset
    #     if (new_offset != query_offset) or (new_duration != query_duration):
    #         print(new_offset, new_duration)
    #         query_offset = new_offset
    #         query_duration = new_duration
    #         offset = new_offset
    #         duration = new_duration
    #     fig, fig_photo = draw_wav(librosa.load(query_wav, offset=offset, duration=duration)[0], vlines=0.01)
    #     start = ("{:0.2f}").format(offset)
    #     end = ("{:0.2f}").format(offset + duration) if (duration is not None) else '[end]'
    #     display_text = get_wav_name(query_wav) + ": " + start + " - " + end
    #     window.Element('__now_playing__').Update("Now Playing: " + display_text + " seconds")
    #     now_playing = query_wav
    #     paused = False


    # if event == "Play" and now_playing and is_wav(now_playing):

    #     if paused:
    #         mixer.music.unpause()
    #         media_start_time = time.time() - (media_end_time - media_start_time)
    #         media_end_time = None
    #         paused = False
    #     # if rewind:
    #     #     mixer.music.unpause()
    #     #     rewind = False
    #     else:
    #         if now_playing_mp3_path:
    #             os.remove(now_playing_mp3_path)
    #         if mp3_fd:
    #             os.close(mp3_fd)
    #         wav_fd, now_playing_wav_path = tempfile.mkstemp(suffix=".wav")
    #         temp_wav, temp_wav_fs = librosa.load(now_playing, offset=offset, duration=duration)
    #         print(now_playing_wav_path)
    #         librosa.output.write_wav(now_playing_wav_path, temp_wav, fs)
    #         mp3_fd, now_playing_mp3_path = tempfile.mkstemp(suffix=".mp3")
    #         # print(now_playing_mp3_path)
    #         # AudioSegment.from_wav(now_playing).export(now_playing_mp3_path, format="mp3")
    #         AudioSegment.from_wav(now_playing_wav_path).export(now_playing_mp3_path, format="mp3")
    #         os.remove(now_playing_wav_path)
    #         os.close(wav_fd)
    #         mixer.music.load(now_playing_mp3_path)
    #         # print(offset)
    #         # mixer.music.play(start=(offset*2))  # todo: figure out why *2 necessary for this format
    #         mixer.music.play()
    #         media_start_time = time.time()
    #         media_end_time = None

    # if mixer.music.get_busy():
    #     if duration:
    #         if mixer.music.get_pos() / 1000 >= duration:
    #             mixer.music.stop()

    # if event == "Pause":
    #     if mixer.music.get_busy():
    #         paused = True
    #         media_end_time = time.time()
    #         mixer.music.pause()

    # if event == "Rewind" and is_wav(now_playing):
    #     mixer.music.stop()
    #     # media_start_time = time.time()
    #     # media_end_time = time.time()
    #     paused = False
    #     print("redraw")
    #     # fig, fig_photo = draw_wav(librosa.load(now_playing, offset=offset, duration=duration)[0], vlines=0.01)
        

    # if mixer.music.get_busy():
    #     if media_end_time:
    #         media_current_time = media_end_time - media_start_time
    #     else:
    #         media_current_time = time.time() - media_start_time
    #     music_playhead = media_current_time * fs
    #     # print(media_current_time)
    #     fig, fig_photo = draw_wav(librosa.load(now_playing, offset=offset, duration=duration)[0], vlines=music_playhead)


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

if now_playing_mp3_path:
    os.remove(now_playing_mp3_path)
if mp3_fd:
    os.close(mp3_fd)

window.Close()
