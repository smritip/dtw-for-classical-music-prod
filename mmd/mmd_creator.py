## Creating MMD files from marking metadata (specific to Pyramix's MediaMarker).
## Copyright (C) 2019 Smriti Pramanick
## Using Dynamic Time Warping to Improve the Classical Music Production Workflow

import xml.etree.ElementTree as ET
from constants import *
from random import *

def make_mmd(timecodes, names, ratings, filename):
	root = ET.Element("MediaMetaData")
	ET.SubElement(root, "TakeName")
	ET.SubElement(root, "TakeNotes")
	marker_list = ET.SubElement(root, "MediaMarkerList")

	for i in range(len(timecodes)):
		marker = ET.SubElement(marker_list, "MediaMarker")
		ET.SubElement(marker, "UID").text = get_uid()
		ET.SubElement(marker, "TimeCode").text = timecodes[i]
		ET.SubElement(marker, "Name").text = names[i]
		ET.SubElement(marker, "Comment")
		ET.SubElement(marker, "Rating").text = ratings[i]

	tree = ET.ElementTree(root)
	tree.write(filename)

def get_uid():
	uids = ["{0:0=3d}".format(randint(0, 255)) for i in range(16)]
	uid = "-".join(uids)
	prefix = "16-"
	uid = prefix + uid
	return uid

def make_10_markers():  # every 5 seconds
	timecodes = [str(fs_bso * (5 * i) * timecode_multiplier_96000) for i in range(10)]
	names = [str(i) for i in range(10)]
	ratings = ['2' for i in range(10)]
	
	make_mmd(timecodes, names, ratings, "10markers.mmd")