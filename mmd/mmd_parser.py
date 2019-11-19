## Parsing marking metadata (specific to Pyramix's MediaMarker) from MMD files.
## Copyright (C) 2019 Smriti Pramanick
## Using Dynamic Time Warping to Improve the Classical Music Production Workflow

import xml.etree.ElementTree as ET
from constants import *

def get_markers(mmd_file):  # uses dictionary data structure

	# read in the file and initialize tree
	tree = ET.parse(mmd_file)
	root = tree.getroot()

	markers = {}
	current_timecode = None

	# TODO(smritip): this assumes a certain format of the MMD file, change to be safer
	for elem in root.iter():
		if elem.tag == 'TimeCode':
			current_timecode = elem.text
		if elem.tag == 'Name':
			markers[current_timecode] = elem.text

	return markers

def get_samples_to_labels(mmd_file):  # uses list data structure

	# read in the file and initialize tree
	tree = ET.parse(mmd_file)
	root = tree.getroot()

	timecodes = []
	labels = []
	ratings = []

	# TODO(smritip): this assumes a certain format of the MMD file, change to be safer
	for elem in root.iter():
		if elem.tag == 'TimeCode':
			timecodes.append(elem.text)
		if elem.tag == 'Name':
			labels.append(elem.text)
		if elem.tag == "Rating":
			ratings.append(elem.text)

	# convert timecodes to samples, and then to times (which unit agnostic to sample rate, etc.)
	samples = [float(tc) * (1 / timecode_multiplier_96000) for tc in timecodes]
	times = [s / fs_bso for s in samples]

	return times, labels, ratings