## Definition of Constants
## Copyright (C) 2019 Smriti Pramanick
## Using Dynamic Time Warping to Improve the Classical Music Production Workflow

# For DTW
fft_len = 4096  # FFT window length
hop_size = 2048  # FFT hop size
fs = 22050  # sample rate

# For Timecode calculation (used with Pyramix)
timecode_multiplier_96000 = 23520
timecode_multiplier_22050 = 102400
fs_bso = 96000