import pyaudio
import numpy as np
import wave
import struct
import time

wav_file ='audio/search_testing/db/mozart_eine_kleine1.wav'
start = 5
length= 5
chunk = 1024

wf = wave.open(wav_file, 'rb')
signal = wf.readframes(-1)
signal = np.fromstring(signal, 'Int16')
p = pyaudio.PyAudio()

stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)


pos = wf.getframerate() * length

signal = signal[start * wf.getframerate() : (start * wf.getframerate()) + pos]

sig = signal[1:chunk]

inc = 0;
data = 0;

count = 0
while data != '':
    data = struct.pack("%dh"%(len(sig)), *list(sig))
    print(data)    
    stream.write(data)
    inc += chunk
    sig = signal[inc : inc + chunk]
    count += 1
    if count % 20 == 0:
	    stream.stop_stream()
	    time.sleep(0.5)
	    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
	                channels=wf.getnchannels(),
	                rate=wf.getframerate(),
	                output=True)

stream.stop_stream()


stream.close()
p.terminate()