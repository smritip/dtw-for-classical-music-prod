import PySimpleGUI as sg

from automatic_marking_transfer import AutomaticMarkingTransfer

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
layout = [[sg.Text('Automatic Marking Transfer', font=("Helvetica", 20))],      
          [sg.Text('Path to reference wav file:', size=(25, 1), font=("Helvetica", 12)), sg.InputText(), sg.FileBrowse()],
          [sg.Text('Path to reference MMD file:', size=(25, 1), font=("Helvetica", 12)), sg.InputText(), sg.FileBrowse()],
          [sg.Text('Path to new wav file:', size=(25, 1), font=("Helvetica", 12)), sg.InputText(), sg.FileBrowse()],
          [sg.Text('Destination folder for new MMD file:', size=(25, 1), font=("Helvetica", 12)), sg.InputText(), sg.FolderBrowse()],
          [sg.Text('Name for new MMD file:', size=(25, 1), font=("Helvetica", 12)), sg.InputText()],
          [sg.ReadButton("Transfer"), sg.Cancel()]]

window = sg.Window('Automatic Marking Transfer').Layout(layout)  

event, values = window.Read()

# Actions
if event == "Transfer":
	ref_wav = values[0]
	ref_mmd = values[1]
	new_wav = values[2]
	new_mmd = values[3] + '/' + values[4]
	amt = AutomaticMarkingTransfer(ref_wav, ref_mmd, new_wav, new_mmd)
	amt.transfer_markings()
else:
	print("Cancelled")