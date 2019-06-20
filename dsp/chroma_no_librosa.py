## Smriti Pramanick
## Using Dynamic Time Warping to Improve the Classical Music Production Workflow

import math
import numpy as np
import librosa
from scipy.io import wavfile
from scipy import signal
from constants import *

def wav_to_chroma(path_to_wav_file, offset=0.0, duration=None):

	# generate wav using wavfile
	wav_fs, wav = wavfile.read(path_to_wav_file)
	if type(wav[0, 0]) == np.int16:
		wav = wav / 2**15
	wav =  np.mean(wav, axis=1)

	assert(wav_fs == fs)
	# TODO: resample if not 22050
	# if wav_fs != fs:
	# 	factor = wav_fs / fs
	# 	print("factor", wav_fs, fs, factor)
	# 	num_samples = len(wav) / factor
	# 	wav = signal.resample(wav, num_samples)

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