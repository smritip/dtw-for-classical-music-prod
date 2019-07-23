## Smriti Pramanick
## Using Dynamic Time Warping to Improve the Classical Music Production Workflow

'''
    Automatic Marking Transfer (AMT)
    Given: 2 audio recordings of the same musical piece ("ref_wav" and "unmarked_wav"),
           1 MMD file with markers for one recording (for "ref_wav", called "ref_mmd")
    Goal: Create an MMD file with the same markers in the correct places for the second recording (for "unmarked_wav")
    How: Use DTW to find points of musical correspondence and use this information to transfer
         markers from one recording to the other (from "ref_wav" to "unmarked_wav")
'''

import numpy as np
from dsp.dtw import get_cost_matrix, run_dtw, find_path
from dsp.chroma_scipy import wav_to_chroma
from mmd.mmd_parser import get_markers, get_samples_to_labels
from mmd.mmd_creator import make_mmd, get_uid
from constants import *

class AutomaticMarkingTransfer():

    def __init__(self, ref_wav, ref_mmd, unmarked_wav, unmarked_mmd):
        self.ref_wav = ref_wav
        self.ref_mmd = ref_mmd
        self.unmarked_wav = unmarked_wav
        self.unmarked_mmd = unmarked_mmd
        self.progress = 0
        self.total_steps = 9
    
    def get_progress(self):
        return self.progress / self.total_steps

    def transfer_markings(self):

        # First, run DTW

        print("\nRunning DTW:\n")
        print("1. Creating chromagrams")
        
        self.progress += 1
        
        ref_chroma = wav_to_chroma(self.ref_wav)
        self.progress += 1
        
        unmarked_chroma = wav_to_chroma(self.unmarked_wav)
        self.progress += 1

        print("2. Creating Cost Matrix")
        C = get_cost_matrix(ref_chroma, unmarked_chroma)
        self.progress += 1
        
        print("3. Creating Accumulated Cost Matrix")
        D, B = run_dtw(C)
        self.progress += 1
        
        print("4. Backtracking to finding DTW path\n")
        path = find_path(B)
        self.progress += 1

        # Then, create new markers for unmarked_wav

        print("Creating new markers:\n")
        print("1. Parsing", self.ref_mmd)

        ref_times, ref_names, ref_ratings = get_samples_to_labels(self.ref_mmd)
        
        # convert ref_times to ref_samples
        ref_samples = [int((t * fs) / hop_size) for t in ref_times]

        self.progress += 1

        print("2. Transferring markers")

        new_samples = []

        for i in range(len(ref_samples)):
            sample_index = 0
            while path[sample_index][0] < ref_samples[i]:  # 0 for ref, 1 for new
                sample_index += 1
                if sample_index == len(path):
                    break
            if sample_index == len(path):
                break
            new_samples.append(path[sample_index][1])

        new_timecodes = [str(s * timecode_multiplier_22050 * hop_size) for s in new_samples]
        new_names = ref_names[:len(new_timecodes)]
        new_ratings = ref_ratings[:len(new_timecodes)]

        self.progress += 1

        print("3. Creating", self.unmarked_mmd, "\n")

        make_mmd(new_timecodes, new_names, new_ratings, self.unmarked_mmd)

        self.progress += 1

        print('Automatic marking transfer complete!\n')

# TODO: instructions and examples on how to run script from command line