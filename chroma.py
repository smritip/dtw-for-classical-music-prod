## Smriti Pramanick
## Using Dynamic Time Warping to Improve the Classical Music Production Workflow

import math
import numpy as np
import librosa
from constants import *

def wav_to_chroma(path_to_wav_file):

	# generate wav using librosa
	wav, wav_fs = librosa.load(path_to_wav_file)
	print("the sampling rate is", wav_fs)
	assert(wav_fs == fs)

	# create chroma (STFT --> spectrogram --> chromagram)
	stft = create_stft(wav)
	chroma = create_chroma(stft)

	return chroma

def create_stft(wav):
	L = fft_len
	H = hop_size

	# use centered window by zero-padding
	x = np.concatenate((np.zeros(int(L / 2)), wav))

	N = len(x)

	num_bins = 1 + int(L / 2)
	num_hops = int(((N - L) / H) + 1)

	stft = np.empty((num_bins, num_hops), dtype=complex)

	M = num_hops

	for m in range(M):
		section = x[(m * H):((m * H) + L)]
		win = section * np.hanning(len(section))
		stft[:, m] = np.fft.rfft(win)

	return stft

def create_chroma(ft, normalize=True):
	spec = np.abs(ft) ** 2
	chromafb = librosa.filters.chroma(fs, fft_len)
	raw_chroma = np.dot(chromafb, spec)
	if not normalize:
		return raw_chroma
	chroma = librosa.util.normalize(raw_chroma, norm=2, axis=0)
	return chroma