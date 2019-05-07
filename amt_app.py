import PySimpleGUI as sg

from app_threading import thread_with_trace
from automatic_marking_transfer import AutomaticMarkingTransfer

global amt

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
layout = [[sg.Text('Automatic Marking Transfer', font=("Helvetica", 20))],      
          [sg.Text('Path to reference wav file:', size=(25, 1), font=("Helvetica", 12)), sg.InputText(), sg.FileBrowse()],
          [sg.Text('Path to reference MMD file:', size=(25, 1), font=("Helvetica", 12)), sg.InputText(), sg.FileBrowse()],
          [sg.Text('Path to new wav file:', size=(25, 1), font=("Helvetica", 12)), sg.InputText(), sg.FileBrowse()],
          [sg.Text('Destination folder for new MMD file:', size=(25, 1), font=("Helvetica", 12)), sg.InputText(), sg.FolderBrowse()],
          [sg.Text('Name for new MMD file:', size=(25, 1), font=("Helvetica", 12)), sg.InputText()],
          [sg.Text('', size=(2, 1))],
          [sg.ReadButton("Transfer"), sg.Cancel(), sg.ReadButton("Close Window")],
          [sg.Text('', size=(2, 1))],
          [sg.ProgressBar(1, orientation='h', size=(60, 18), key='progbar')]]

window = sg.Window('Automatic Marking Transfer').Layout(layout)

# App logic

amt = None

while True:

	event, values = window.Read(timeout=100)

	if amt:
		window.Element('progbar').UpdateBar(amt.get_progress())

	if event == "Transfer":
		
		if values[0] == "":  # default for testing
			ref_wav = "bso_files/4-27.wav"
			ref_mmd = "bso_files/4-27.mmd"
			new_wav = "bso_files/4-28.wav"
			new_mmd = "testing/test.mmd"
		else:
			ref_wav = values[0]
			ref_mmd = values[1]
			new_wav = values[2]
			new_mmd = values[3] + '/' + values[4]

		amt = AutomaticMarkingTransfer(ref_wav, ref_mmd, new_wav, new_mmd)

		# start a new thread to carry out AMT (so it can be pre-empted by a cancel)
		amt_thread = thread_with_trace(target = amt.transfer_markings)
		amt_thread.start()

	elif event == "Cancel" or event == "Close Window":
		window.Element('progbar').UpdateBar(0)
		if amt:
			amt = None
			amt_thread.kill() 
			amt_thread.join() 
			if not amt_thread.isAlive():
				print("\nCancelled AMT")
		if event == "Close Window":
			break

window.Close()