## Creating chromagrams from wave files, using scipy.io's wavfile library.
## Copyright (C) 2019 Smriti Pramanick
## Using Dynamic Time Warping to Improve the Classical Music Production Workflow

import math
import numpy as np
from scipy.io import wavfile
from constants import *
# import librosa

def load_wav(path_to_wav_file, offset=0.0, duration=None):
	# # generate wav using wavfile
	# wav_fs, wav = wavfile.read('bso_files/test/4-27_crop.wav')
	# wav_fs, wav = wavfile.read(path_to_wav_file)  # TODO: bug w wavs that have metadata in chunks...
	wav_fs, wav = wavfile.read(path_to_wav_file)
	if type(wav[0, 0]) == np.int16:
			wav = wav / 2**15
	# if type(new_wav.dtype) == np.int16:
	# 	new_wav = new_wav / 2**15
	wav = np.mean(wav, axis=1)

	assert(wav_fs == fs)
	# TODO: resample if not 22050 (use scipy.signal.resample)

	# print(len(wav))

	if offset:
		num_samples = int(offset * fs)
		wav = wav[num_samples:]

	if duration:
		num_samples = int(duration * fs)
		wav = wav[:num_samples]

	# TODO: offset and duration without loading the whole file
	

	# for checking:
	# wav2, fs2 = librosa.load(path_to_wav_file, offset=offset, duration=duration)
	# print(wav2 == wav)

	return wav

def wav_to_chroma(path_to_wav_file, offset=0.0, duration=None):
	wav = load_wav(path_to_wav_file, offset, duration)
	print("wav", wav)
	# create chroma (STFT --> spectrogram --> chromagram)
	stft = create_stft(wav)
	print("stft", stft)
	chroma = create_chroma(stft)

	print("chroma", chroma)

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

def pitch_to_freq(p):
	return (2**((p - 69.)/12.)) * 440.

def bins_of_pitch(p):
	freq_min = pitch_to_freq(p - 0.5)
	freq_max = pitch_to_freq(p + 0.5)
	out = []
	for k in range(1, int(fft_len/2) +1):
		tf = fs / float(fft_len) * k
		if freq_min <= tf < freq_max:
			out.append(k)
	return out

def spec_to_pitch_fb(start_pitch, end_pitch):
	pitch_range = end_pitch - start_pitch + 1
	num_bins = int(fft_len/2) + 1
	c_fp = np.zeros((pitch_range, num_bins))
	for m in range(pitch_range):
		bins = bins_of_pitch(m + start_pitch)
		for n in bins:
			c_fp[m, n] = 1
			
	return c_fp	

def normalize_matrix(mtx):
	col_norms = np.linalg.norm(mtx, axis=0, ord=2) # ord = 2 means L2 norm
	return mtx.astype(np.float) / col_norms

def create_chroma(ft, normalize=True):
	spec = np.abs(ft) ** 2
	c_fp = spec_to_pitch_fb(0, 127)
	
	pgram = np.dot(c_fp, spec)
	
	c_pc = np.tile(np.identity(12), 11)[:, 0:128]
	
	c = np.dot(c_pc, pgram)

	c = np.log10(1 + 10 * c)

	if normalize:
		c = normalize_matrix(c)
	
	return c