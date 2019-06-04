import PySimpleGUI as sg
import os
import librosa
import time

from pygame import mixer

from app_threading import thread_with_trace
from audio_search_system import AudioSearchSystem
from display_wav import create_figure, draw_figure
from constants import *

global search_system

# UI elements
image_width = 3
image_height = 1.5

layout = [[sg.Text('')],
          [sg.Text('Audio Search System', font=("Helvetica", 20))],
          [sg.Text('')],      
          [sg.Text('Path to query wav file:', size=(16, 1), font=("Helvetica", 12)), sg.InputText(size=(80, 1), key="__query__"), sg.FileBrowse()],
          [sg.Text('Start time (mm:ss):', size=(14, 1), font=("Helvetica", 12)), sg.InputText(size=(4, 1), justification='right', key="__start_mins__"), sg.Text(':', size=(1, 1), font=("Helvetica", 12)), sg.InputText(size=(4, 1), justification='right', key="__start_secs__"), sg.Text('', size=(5, 1)),
           sg.Text('End time (mm:ss):', size=(14, 1), font=("Helvetica", 12)), sg.InputText(size=(4, 1), justification='right', key="__end_mins__"), sg.Text(':', size=(1, 1), font=("Helvetica", 12)), sg.InputText(size=(4, 1), justification='right', key="__end_secs__")],
          [sg.Canvas(size=(image_width*100, image_height*100), key='canvas'),
           sg.ReadButton('', image_filename='icons/play_reduced.png', image_size=(30, 30), border_width=0, key='Play'),
           sg.ReadButton('', image_filename='icons/pause_reduced.png', image_size=(30, 30), border_width=0, key='Pause'),
           sg.ReadButton('', image_filename='icons/rewind_reduced.png', image_size=(30, 30), border_width=0, key='Rewind')],
          [sg.Text('Folder with wav files to search through:', size=(28, 1), font=("Helvetica", 12)), sg.InputText(key="__db__"), sg.FolderBrowse()],
          [sg.Text('Number of matches to find (per file):', size=(28, 1), font=("Helvetica", 12)), sg.InputText(key="__num__")],
          [sg.ReadButton("Search"), sg.Cancel(), sg.ReadButton("Close Window")],
          [sg.Text('', size=(2, 1))],
          [sg.ProgressBar(1, orientation='h', size=(60, 18), key='progbar')],
          [sg.Text('Matches:', font=("Helvetica", 12))],
          [sg.Text('', size=(50, 18), font=("Helvetica", 14), key='_OUTPUT_')]]

window = sg.Window('Audio Search System').Layout(layout).Finalize() 

# App logic

search_system = None

def run_search():
    print("\nSearching")
    matches = search_system.search()
    matches_result = search_system.print_matches(matches)
    window.FindElement('_OUTPUT_').Update(matches_result)

def is_wav(file):
    return file[-4:] == ".wav"

def time_to_secs(mins, secs):
    return (int(mins) * 60) + int(secs)


# initializations
query_wav = ""
offset = 0.0
duration = None
start_time = None
end_time = None

fig, figure_x, figure_y, figure_w, figure_h = create_figure(0, image_width, image_height)
fig_photo = draw_figure(window.FindElement('canvas').TKCanvas, fig)

mixer.init(channels=2)
query_channel = mixer.Channel(0)
paused = False
s = None
channel_start_time = None
channel_end_time = None
rewind = None

# defaults
# query_wav = "audio/search_testing/query/mozart_query.wav"
# db_dir = "audio/search_testing/db"
# num_matches = 5

while True:     

    event, values = window.Read(timeout=100)
  
    if values['__query__'] != query_wav:  # new query wav, so reload wav file
        query_wav = values['__query__']
        fig, figure_x, figure_y, figure_w, figure_h = create_figure(librosa.load(query_wav)[0], width=image_width, height=image_height, vlines=0)
        fig_photo = draw_figure(window.FindElement('canvas').TKCanvas, fig)
        paused = False  ## TODO: check this      
        
    if query_wav != "":
        if values['__start_secs__'] != "":
            start_secs = values['__start_secs__']
            if values['__start_mins__'] == "":
                start_mins = 0
            else:
                start_mins = values['__start_mins__']
            query_time = time_to_secs(start_mins, start_secs)
            if start_time != query_time:
                start_time = query_time
                # print(start_time)
                offset = start_time
                if end_time:
                    if end_time > start_time:
                        duration = end_time - start_time
                print(offset, duration)
                fig, figure_x, figure_y, figure_w, figure_h = create_figure(librosa.load(query_wav, offset=offset, duration=duration)[0], width=image_width, height=image_height, vlines=0)
                fig_photo = draw_figure(window.FindElement('canvas').TKCanvas, fig)
                paused = False

        if values['__end_secs__'] != "":
            end_secs = values['__end_secs__']
            if values['__end_mins__'] == "":
                end_mins = 0
            else:
                end_mins = values['__end_mins__']
            query_time = time_to_secs(end_mins, end_secs)
            if end_time != query_time:
                end_time = query_time
                # print(end_time)
                if start_time != None:
                    if end_time > start_time:
                        duration = end_time - start_time
                        print(offset, duration)
                        fig, figure_x, figure_y, figure_w, figure_h = create_figure(librosa.load(query_wav, offset=offset, duration=duration)[0], width=image_width, height=image_height, vlines=0)
                        fig_photo = draw_figure(window.FindElement('canvas').TKCanvas, fig)
                        paused = False

    if search_system:
        window.Element('progbar').UpdateBar(search_system.get_progress())   


    # if event == "Play" and is_wav(query_wav):
    #     if paused:
    #         query_channel.unpause()
    #         channel_start_time = time.time() - (channel_end_time - channel_start_time)
    #         channel_end_time = None
    #         paused = False
    #     else:
    #         if rewind:
    #             query_channel.unpause()
    #             rewind = False
    #         s = mixer.Sound(query_wav)
    #         channel_start_time = time.time()
    #         channel_end_time = None
    #         if duration:
    #             # print(duration)
    #             query_channel.play(s, maxtime=duration*1000)
    #         else:
    #             query_channel.play(s)
    #     # mixer.music.load(query_wav)
    #     # mixer.music.play()

    if event == "Play" and is_wav(query_wav):

        if paused:
            mixer.music.unpause()
            channel_start_time = time.time() - (channel_end_time - channel_start_time)
            channel_end_time = None
            paused = False
        else:
            # if rewind:
            #     query_channel.unpause()
            #     rewind = False
            mixer.music.load(query_wav)
            mixer.music.play()
            channel_start_time = time.time()
            channel_end_time = None

    if mixer.music.get_busy():
        if duration:
            if mixer.music.get_pos() / 1000 >= duration:
                mixer.music.stop()

    if event == "Pause":
        if mixer.music.get_busy():
            paused = True
            channel_end_time = time.time()
            # pause_offset = s.get_pos()
            # print(pause_offset)
            mixer.music.pause()

    if event == "Rewind" and is_wav(query_wav):
        query_channel.stop()
        paused = False
        s = mixer.Sound(query_wav)
        if duration:
            query_channel.play(s, maxtime=duration*1000)
        else:
            query_channel.play(s)
        query_channel.pause()
        rewind = True

    # TODO: keep track of offset
    if mixer.music.get_busy():
        if channel_end_time:
            channel_current_time = channel_end_time - channel_start_time
        else:
            channel_current_time = time.time() - channel_start_time
        # if offset:
        #     channel_current_time += offset
        music_playhead = channel_current_time * fs
        print(channel_current_time)
        # fig, figure_x, figure_y, figure_w, figure_h = create_figure(librosa.load(query_wav, offset=offset, duration=duration)[0], width=image_width, height=image_height, vlines=music_playhead)
        # fig_photo = draw_figure(window.FindElement('canvas').TKCanvas, fig)

    if event == "Search":


        # mixer.init()
        # mixer.music.load("audio/search_testing/query/mozart_query.wav")
        # mixer.music.play()


        
        query_wav = values['__query__']
        db_dir = values['__db__']
        num_matches = int(values['__num__'])
        
        print(query_wav)
        print(db_dir)
        print(num_matches)

        db = []
        for file in os.listdir(db_dir):
            if file.endswith(".wav"):
                db.append(db_dir + "/" + file)
        
        search_system = AudioSearchSystem(query_wav, db, num_matches)

        search_thread = thread_with_trace(target = run_search)
        search_thread.start()
    
    elif event == "Cancel" or event == "Close Window" or event is None:
        window.Element('progbar').UpdateBar(0)
        if search_system:
            search_system = None
            window.FindElement('_OUTPUT_').Update("")
            search_thread.kill() 
            search_thread.join() 
            if not search_thread.isAlive():
                print("\nCancelled Search")
        if event == "Close Window" or event is None:
            break  

window.Close()
