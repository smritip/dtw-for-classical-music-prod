# source: https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Matplotlib.py

import PySimpleGUI as sg

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasAgg
import matplotlib.backends.tkagg as tkagg
import tkinter as Tk

import numpy as np
import matplotlib.pyplot as plt

import librosa

from matplotlib.ticker import NullFormatter  # useful for `logit` scale

def create_figure(wav_file, width=2, height=2, vlines=None, ymin=-1, ymax=1):  ## todo: scale ymin/ymax to song
	# plt.figure(figsize=(width,height))
	plt.figure(figsize=(width, height))
	plt.plot(wav_file)
	plt.xticks(range(0)," ")
	plt.yticks(range(0)," ")
	if vlines:
		plt.vlines(vlines, ymin, ymax)
	# plt.axis('off')
	# plt.grid(True)

	fig = plt.gcf()      # if using Pyplot then get the figure from the plot
	# fig.set_size_inches(width, height)
	figure_x, figure_y, figure_w, figure_h = fig.bbox.bounds
	# figure_w, figure_h = width, height
	plt.close()
	# print(figure_w, figure_h)
	return fig


def draw_figure(canvas, figure, loc=(0, 0)):
	""" Draw a matplotlib figure onto a Tk canvas
	loc: location of top-left corner of figure on canvas in pixels.
	Inspired by matplotlib source: lib/matplotlib/backends/backend_tkagg.py
	"""
	figure_canvas_agg = FigureCanvasAgg(figure)
	figure_canvas_agg.draw()
	figure_x, figure_y, figure_w, figure_h = figure.bbox.bounds
	figure_w, figure_h = int(figure_w), int(figure_h)
	# print(figure_w, figure_h)
	photo = Tk.PhotoImage(master=canvas, width=figure_w, height=figure_h)
	canvas.create_image(loc[0] + figure_w/2, loc[1] + figure_h/2, image=photo)
	tkagg.blit(photo, figure_canvas_agg.get_renderer()._renderer, colormode=2)
	return photo

# example use in app:

# fig, figure_x, figure_y, figure_w, figure_h = create_figure(librosa.load("audio/mozart_query.wav")[0])
# # print(figure_w, figure_h)

# # define the window layout
# layout = [[sg.Text('Plot test', font='Any 18')],
#           [sg.Canvas(size=(figure_w, figure_h), key='canvas')],
#           [sg.OK(pad=((figure_w / 2, 0), 3), size=(4, 2))]]

# # create the form and show it without the plot
# window = sg.Window('Demo Application - Embedding Matplotlib In PySimpleGUI', force_toplevel=True).Layout(layout).Finalize()

# # add the plot to the window
# fig_photo = draw_figure(window.FindElement('canvas').TKCanvas, fig)

# # show it all again and get buttons
# event, values = window.Read()
