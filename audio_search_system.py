## Smriti Pramanick
## Using Dynamic Time Warping to Improve the Classical Music Production Workflow

'''
    Audio Search System
    Given: 1 audio snippet: the query (wav file)
    	   List of wav files to search through: the database (list of wav files)
		   Number of matches to search for (integer)
    Goal: Find the query audio in the database (return matches as a list of files and corresponding timestamps)
    How: Using DTW for audio matching (see 'dtw_match_cost' in dsp.dtw)
'''

# TODO(smritip): write class (like with AMT) and search through list of wav files (not just one)
# TODO(smritip): do we want to run on each db file, or combine and run on larger one

import numpy as np
from constants import *
from dsp.dtw import get_cost_matrix, dtw_match_cost
from dsp.chroma import wav_to_chroma

STEPS = ((-1, -1), (-1, -2), (-2, -1))

def find_top_n_troughs(x, n, win_hlen):
    troughs = []
    signal = x.copy()
    maximum = np.amax(signal)
    for i in range(n):
        minimum_index = np.argmin(signal)
        troughs.append(minimum_index)
        left = max(minimum_index - win_hlen, 0)
        right = min(minimum_index + win_hlen, len(signal) - 1)
        signal[left : right] = maximum
    return troughs, signal

def get_match_regions(d_dtw, B, num_matches):
    N = B.shape[0]
    end_pts, new_sig = find_top_n_troughs(d_dtw, num_matches, N)
    matches = []
    for pt in end_pts:
        current = (N-1, pt)
        while current[0] >= 0:
            ptr = B[current[0], current[1]]
            step = STEPS[ptr]
            current = (current[0] + step[0], current[1] + step[1])
        ff = fs / hop_size
        start = current[1] / ff
        end = pt / ff
        cost = d_dtw[pt]
        matches.append((start, end, cost))
        
    return matches, new_sig

chroma_db = wav_to_chroma("audio/mozart_eine_kleine1.wav")
chroma_query = wav_to_chroma("audio/mozart_query.wav")

C = get_cost_matrix(chroma_query, chroma_db)
D, B = dtw_match_cost(C, steps=STEPS)

# last row of D is matching function
matching = D[-1, :]

matches, new_sig = get_match_regions(matching, B, 2)
print(matches)