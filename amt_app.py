import PySimpleGUI as sg

from app_threading import thread_with_trace
from automatic_marking_transfer import AutomaticMarkingTransfer

global amt

# UI elements
layout = [[sg.Text('')],
		  [sg.Text('Automatic Marking Transfer', font=("Helvetica", 20))],  ## TODO: center text with function
          [sg.Text('')],
          [sg.Text('Path to reference wav file:', size=(20, 1), font=("Helvetica", 12)), sg.InputText(size=(80, 1)), sg.FileBrowse()],
          [sg.Text('Path to unmarked wav file:', size=(20, 1), font=("Helvetica", 12)), sg.InputText(size=(80, 1)), sg.FileBrowse()],
          [sg.Text('')],
          [sg.ReadButton("Transfer"), sg.Cancel(), sg.ReadButton("Close Window")],
          [sg.Text('')],
          [sg.ProgressBar(1, orientation='h', size=(60, 15), key='progbar')],
          [sg.Text('')]]

window = sg.Window('Automatic Marking Transfer').Layout(layout)

# App logic

amt = None

def wav_to_mmd_filename(wav):
	wav_path_parts = wav.split("/")
	mmd_dir = "/".join(wav_path_parts[:-1]) + "/"
	mmd_filename = wav_path_parts[-1].split(".")[0]
	mmd = mmd_dir + mmd_filename + ".mmd"
	return mmd

while True:

	event, values = window.Read(timeout=100)

	if amt:
		window.Element('progbar').UpdateBar(amt.get_progress())

	if event == "Transfer":
		
		if values[0] == "":  # default for testing
			ref_wav = "bso_files/test/4-27_crop.wav"
			ref_mmd = "bso_files/test/4-27.mmd"
			unmarked_wav = "bso_files/test/4-28_crop.wav"
			unmarked_mmd = "bso_files/test/4-28.mmd"
		else:
			ref_wav = values[0]
			ref_mmd = wav_to_mmd_filename(ref_wav)
			unmarked_wav = values[1]
			unmarked_mmd = wav_to_mmd_filename(unmarked_wav)

		amt = AutomaticMarkingTransfer(ref_wav, ref_mmd, unmarked_wav, unmarked_mmd)

		# start a new thread to carry out AMT (so it can be pre-empted by a cancel)
		amt_thread = thread_with_trace(target = amt.transfer_markings)
		amt_thread.start()

	elif event == "Cancel" or event == "Close Window" or event is None:
		window.Element('progbar').UpdateBar(0)
		if amt:
			amt = None
			amt_thread.kill() 
			amt_thread.join() 
			if not amt_thread.isAlive():
				print("\nCancelled AMT")
		if event == "Close Window" or event is None:
			break

window.Close()