import numpy as np
from array import array
import wave
import sys
import socket
import errno
#from scipy import signal as sgnl

fullfilename = sys.argv[1]
sys.stderr.close()

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
try:
	for passnum in range(numpasses):# + (numframes%samplesize)):
		rawbuffer = array('h')
		#read 1024 frames from input buffer
		rawbuffer.frombytes(input.readframes(samplesize))

		#If there are multiple channels we sum them down to one
		rawchannels = np.array(rawbuffer)
		if numchannels == 2:
			ch1 = rawchannels[0:samplesize*numchannels:numchannels]
			ch2 = rawchannels[1:samplesize*numchannels:numchannels]
			#ch1 = ch1 - (sum(ch1)/samplesize)
			#ch2 = ch2 - (sum(ch2)/samplesize)
			signal = np.array([(sum(ch)) for ch in zip(ch1,ch2)])
		else:
			signal = rawchannels
		#signal = sgnl.detrend(signal,type='constant')
		#now we high pass filter to remove the DC component
		hpfourier = np.fft.rfft(signal)
		#set the mean to 0
		hpfourier[0] = 0
		#reproduce the signal without DC component
		hpsignal = np.fft.irfft(hpfourier)

		#apply the window
		signal = hpsignal * window
		#fft the high passed data
		fourier = np.fft.rfft(signal)
		#compute the magnitude of the real and imaginary parts of the results
		#and scale for window usage
		mags = np.abs(fourier) * 2 / np.sum(window)
		#convert to DBFS
		dbfsbins = 20 * np.log10(mags/dbfsref)

		#send bins to display process
		for b in range(samplesize//2):
			if dbfsbins[b+1] > -0.00001:
				print(str(0.0) + " ")
			elif dbfsbins[b+1] == float("-Inf"):
				print(str(-150.0) + " ")
			else:
				print(str(dbfsbins[b+1]) + " ")
except socket.error as e:
	if e.errno != errno.EPIPE:
		error = e

#END OF MAIN LOOP
