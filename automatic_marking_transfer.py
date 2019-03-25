## Smriti Pramanick
## Using Dynamic Time Warping to Improve the Classical Music Production Workflow

'''
    Automatic Marking Trasnfer (AMT)
    Given: 2 audio recordings of the same musical piece ("ref_wav" and "new_wav"),
           1 MMD file with markers for one recording (for "ref_wav", called "ref_mmd")
    Goal: Create an MMD file with the same markers in the correct places for the second recording (for "new_wav")
    How: Use DTW to find points of musical correspondence and use this information to transfer
         markers from one recording to the other (from "ref_wav" to "new_wav")
'''

import numpy as np
from dsp.dtw import get_cost_matrix, run_dtw, find_path
from dsp.chroma import wav_to_chroma
from mmd.mmd_parser import get_markers, get_samples_to_labels
from mmd.mmd_creator import make_mmd, get_uid

class AutomaticMarkingTransfer():

    def __init__(self):  # interactive init method from command line
        print("")
        self.ref_wav = input("Provide a path for the reference recording: ")
        print("")
        self.ref_mmd = input("Provide a path for the reference MMD file: ")
        print("")
        self.new_wav = input("Provide a path for the new recording: ")
        print("")
        self.new_mmd = input("Provide a path for the new MMD file (to be created): ")
        print("")

    def transfer_markings(self):

        # First, run DTW

        print("Running DTW:\n")
        print("1. Creating chromagrams")
        ref_chroma = wav_to_chroma(self.ref_wav)
        new_chroma = wav_to_chroma(self.new_wav)

        print("2. Creating Cost Matrix")
        C = get_cost_matrix(ref_chroma, new_chroma)

        print("3. Creating Accumulated Cost Matrix")
        D, B = run_dtw(C)

        print("4. Backtracking to finding DTW path\n")
        path = find_path(B)

        # Then, create new markers for new_wav

        print("Creating new markers:\n")
        print("1. Parsing", self.ref_mmd)

        ref_times, ref_names, ref_ratings = get_samples_to_labels(self.ref_mmd)
        
        # convert ref_times to ref_samples
        ref_samples = [int((t * 22050) / 2048) for t in ref_times]

        print("2. Transferring markers")

        new_samples = []

        for i in range(len(ref_samples)):
            sample_index = 0
            while path[sample_index][0] < ref_samples[i]:
                sample_index += 1
                if sample_index == len(path):
                    break
            if sample_index == len(path):
                break
            new_samples.append(path[sample_index][1])

        new_timecodes = [str(s * 102400 * 2048) for s in new_samples]
        new_names = ref_names[:len(new_timecodes)]
        new_ratings = ref_ratings[:len(new_timecodes)]

        print("3. Creating", self.new_mmd, "\n")

        make_mmd(new_timecodes, new_names, new_ratings, self.new_mmd)

        print('Automatic narking transfer complete!\n')

amt = AutomaticMarkingTransfer()
amt.transfer_markings()