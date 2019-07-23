# source: https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Matplotlib.py

import PySimpleGUI as sg

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasAgg
import matplotlib.backends.tkagg as tkagg
import tkinter as Tk

import matplotlib.pyplot as plt

def create_figure(wav_file, width=2, height=2, vlines=None, ymin=-1, ymax=1):  ## todo: scale ymin/ymax to song
	# plt.figure(figsize=(width,height))
	plt.figure(figsize=(width, height))
	plt.plot(wav_file)
	plt.xticks(range(0)," ")
	plt.yticks(range(0)," ")
	if vlines:
		plt.vlines(vlines, ymin, ymax)

	fig = plt.gcf()      # if using Pyplot then get the figure from the plot
	figure_x, figure_y, figure_w, figure_h = fig.bbox.bounds
	plt.close()
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
	photo = Tk.PhotoImage(master=canvas, width=figure_w, height=figure_h)
	canvas.create_image(loc[0] + figure_w/2, loc[1] + figure_h/2, image=photo)
	tkagg.blit(photo, figure_canvas_agg.get_renderer()._renderer, colormode=2)
	return photo