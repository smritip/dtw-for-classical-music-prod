## Smriti Pramanick
## Using Dynamic Time Warping to Improve the Classical Music Production Workflow

import numpy as np
from dtw import get_cost_matrix, run_dtw, find_path
from chroma import wav_to_chroma
from mmd_parser import get_markers, get_samples_to_labels

# First, run DTW

# a = input("What is piece a? ")
# b = input("What is piece b? ")
a = 'bso_files/4-27_cropped.wav'
b = 'bso_files/4-27_cropped.wav'

print("creating chroma")
a_chroma = wav_to_chroma(a)
b_chroma = wav_to_chroma(b)

print("getting cost matrix")
C = get_cost_matrix(a_chroma, b_chroma)

print("running dtw")
D, B = run_dtw(C)

print("finding path")
path = find_path(B)
print(path)

# Then, create new markers for whole piece (using path and old markers)

a_samples, a_times, a_labels = get_samples_to_labels('bso_files/4-27.mmd')
# markers = get_markers(a)

print(a_samples)
print(a_times)
print(a_labels)