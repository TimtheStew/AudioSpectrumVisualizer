import numpy as np
from array import array
import wave
import sys
import socket
import errno

fullfilename = sys.argv[1]

#get the wave object
input = wave.open(fullfilename,'r')
#and all the baggage
params = input.getparams()
numframes=params.nframes
samplerate=params.framerate
samplewidth=params.sampwidth
numchannels=params.nchannels
#we're doing a 1024 pt fft
samplesize = 1024
#refernce value for calculating DBFS from 16 bit wav format
dbfsref = 32768
#anything above that isn't really applicable
numpasses = numframes//samplesize
#duration of the song (in seconds)
songduration = params.nframes // samplerate
settings = np.seterr(all='ignore')

#this will use almost all the samples, though it may leave at worse 1023 unread
#at (usually) less than 1/40th of a second, 1023 frames aint no thang
windowtype = "Hanning"
if (windowtype == "Hanning"):
	window = np.hanning(samplesize)
elif (windowtype == "Hamming"):
	window = np.hamming(samplesize)
elif (windowtype == "Blackman"):
	window = np.blackman(samplesize)
elif (windowtype == "Bartlett"):
	window = np.bartlett(samplesize)
else:
	window = np.zeros(samplesize)
for passnum in range(numpasses):# + (numframes%samplesize)):
	rawbuffer = array('h')
	#read 1024 frames from input buffer
	rawbuffer.frombytes(input.readframes(samplesize))

	#If there are multiple channels we sum them down to one
	rawchannels = np.array(rawbuffer)
	if numchannels == 2:
		ch1 = rawchannels[0:samplesize*numchannels:numchannels]
		ch2 = rawchannels[1:samplesize*numchannels:numchannels]
		ch1 = ch1 - (sum(ch1)/samplesize)
		ch2 = ch2 - (sum(ch2)/samplesize)
		signal = np.array([(sum(ch)) for ch in zip(ch1,ch2)])
	else:
		signal = rawchannels

	signal = signal * window
	fourier = np.fft.rfft(signal)
	mags = np.abs(fourier) * 2 / np.sum(window)
	dbfsbins = 20 * np.log10(mags/dbfsref)

	#write bins to file
	for b in range(samplesize//2):
		try:
			if dbfsbins[b+1] > -0.00001:
				print(str(0.0) + " ")
			elif dbfsbins[b+1] == float("-Inf"):
				print(str(-150.0) + " ")
			else:
				print(str(dbfsbins[b+1]) + " ")
		except socket.error as e:
			if e.errno != errno.EPIPE:
				raise
#END OF MAIN LOOP
