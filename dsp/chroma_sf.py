## Smriti Pramanick
## Using Dynamic Time Warping to Improve the Classical Music Production Workflow

import math
import numpy as np
# from scipy.io import wavfile
import soundfile as sf
from constants import *

def wav_to_chroma(path_to_wav_file, offset=0.0, duration=None, dtype=np.float32):

    print("using soundfile")

    with sf.SoundFile(path_to_wav_file) as sf_desc:
        sr_native = sf_desc.samplerate
        if offset:
            # Seek to the start of the target read
            sf_desc.seek(int(offset * sr_native))
        if duration is not None:
            frame_duration = int(duration * sr_native)
        else:
            frame_duration = -1
        # Load the target number of frames, and transpose to match librosa form
        wav = sf_desc.read(frames=frame_duration, dtype=dtype, always_2d=False).T

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