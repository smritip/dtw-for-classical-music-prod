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

# TODO(smritip): do we want to run on each db file, or combine and run on larger one
# TODO(smritip): do we want to build up db for a project and then just have queries after
# TODO(smritip): specify or calculate matches per file (maybe based on length)

import numpy as np
from constants import *
from dsp.dtw import get_cost_matrix, dtw_match_cost, get_match_regions
from dsp.chroma import wav_to_chroma

class AudioSearchSystem():

	def __init__(self, query_wav, db, num_matches=5):
		self.query_wav = query_wav
		self.db = db
		self.num_matches = num_matches  ## per file matches

	def search(self):
		chroma_query = wav_to_chroma(self.query_wav)

		matches_dict = {}

		# search through each wav file in db for num_matches matches:
		for wav in self.db:
			chroma_db = wav_to_chroma(wav)
			C = get_cost_matrix(chroma_query, chroma_db)
			D, B = dtw_match_cost(C)
			# last row of D is matching function
			matching = D[-1, :]
			matches = get_match_regions(matching, B, self.num_matches)
			matches_dict[wav] = matches

		return matches_dict

	def print_matches(self, matches_dict):
		result = {self.format_wav_filename(wav) : [self.format_match(m) for m in matches_dict[wav]] for wav in matches_dict}
		print(result)
		return result

	def format_wav_filename(self, wav_file):
		return wav_file.split("/")[-1]

	def format_time(self, secs):
		# TODO(smritip): check to see if time granularity is enough
		return str(int(secs / 60)) + ":" + str(int(secs % 60))

	def format_match(self, match):
		return self.format_time(match[0]) + " - " + self.format_time(match[1])

## Testing from the command line:
# search_system = AudioSearchSystem("audio/mozart_query.wav", ["audio/mozart_eine_kleine1.wav"], 2)
# matches = search_system.search()
# search_system.print_matches(matches)