## Smriti Pramanick
## Using Dynamic Time Warping to Improve the Classical Music Production Workflow

import numpy as np
from dtw import get_cost_matrix, run_dtw, find_path
from chroma import wav_to_chroma
from mmd_parser import get_markers, get_samples_to_labels
from mmd_creator import make_mmd, get_uid

# First, run DTW

# a = input("What is piece a? ")
# b = input("What is piece b? ")
# a = 'bso_files/4-27_cropped.wav'
# b = 'bso_files/4-27_cropped.wav'

# print("creating chroma")
# a_chroma = wav_to_chroma(a)
# b_chroma = wav_to_chroma(b)

# print("getting cost matrix")
# C = get_cost_matrix(a_chroma, b_chroma)

# print("running dtw")
# D, B = run_dtw(C)

# print("finding path")
# path = find_path(B)
# print(path)

# # Then, create new markers for whole piece (using path and old markers)

# a_samples, a_times, a_labels = get_samples_to_labels('bso_files/4-27.mmd')
# # markers = get_markers(a)

# print(a_samples)
# print(a_times)
# print(a_labels)

def get_new_marker(sample, gt_times, gt_timecodes, gt_names):
    # convert sample to time
    time = sample * (2048 / 22050.)
    for i in range(len(gt_times)):
        if i == 0:
            if time <= gt_times[i]:
                if gt_times[i] != 0:
                    frac = float(gt_times[i] - time) / (gt_times[i] - 0)
                else:
                    frac = 0
                return (gt_beats[i] - frac, gt_labels[0])
        else:
            if gt_times[i-1] <= time <= gt_times[i]:
                frac = float(gt_times[i] - time) / (gt_times[i] - gt_times[i-1])
                return (gt_beats[i] - frac, gt_labels[i-1])

    return (None, None)

a = 'bso_files/4-27_crop.wav'
b = 'bso_files/4-28_crop.wav'

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
# print(path[0][0])

# Then, create new markers for whole piece (using path and old markers)

a_times, a_names, a_ratings = get_samples_to_labels('bso_files/4-27.mmd')
# markers = get_markers(a)

# print(a_samples)
print(a_times)
# print(a_names)

a_samples = [int((t * 22050) / 2048) for t in a_times]
print(a_samples)

b_samples = []

for i in range(len(a_samples)):
	sample_index = 0
	while path[sample_index][0] < a_samples[i]:
		print(sample_index, i)
		sample_index += 1
		if sample_index > len(path):
			break
	print(i)
	if sample_index > len(path):
			break
	b_samples = path[sample_index][1]

# assert(len(b_samples) == len(a_names))

b_timecodes = [s * 102400 for s in b_samples]
b_names = a_names[:len(b_timecodes)]
b_ratings = a_ratings[:len(b_timecodes)]

make_mmd(b_timecodes, b_names, b_ratings, "test.mmd")