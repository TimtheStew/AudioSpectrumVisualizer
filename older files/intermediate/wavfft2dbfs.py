import numpy as np
from array import array
import wave
import time
import sys
import subprocess
import ntpath
import os

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

fullfilename = sys.argv[1]
datafilename = path_leaf(fullfilename) + "fftdata.txt"

start = time.time()
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


#open the file
fftout = open(datafilename,'w')

#first line of fft data file is the duration of the song in seconds
fftout.write(str(songduration) +'\n')
#second line of fft data file is the num of passes (lines of data in the file)
fftout.write(str(numpasses)+'\n')
#the third line is the number of bins (values on each line, seperated by spaces)
fftout.write(str(samplesize//2)+'\n')

#this will use almost all the samples, though it may leave at worse 1023 unread
#at (usually) less than 1/40th of a second, 1023 frames aint no thang
window = np.blackman(samplesize)
for passnum in range(numpasses):# + (numframes%samplesize)):
	rawbuffer = array('h')
	#read 1024 frames from input buffer
	rawbuffer.frombytes(input.readframes(samplesize))

	#If there are multiple channels we sum them down to one
	rawchannels = np.array(rawbuffer)
	if numchannels == 2:
		ch1 = rawchannels[0:samplesize*numchannels:numchannels]
		ch2 = rawchannels[1:samplesize*numchannels:numchannels]
		signal = np.array([(sum(ch)/2) for ch in zip(ch1,ch2)])
	else:
		signal = rawchannels

	signal = signal * window
	fourier = np.fft.rfft(signal)
	mags = np.abs(fourier) * 2 / np.sum(window)
	dbfsbins = 20 * np.log10(mags/dbfsref)

	#write bins to file
	for b in range(samplesize//2):
		if dbfsbins[b+1] > -0.00001:
			fftout.write(str(0.0) + " ")
		elif dbfsbins[b+1] == float("-Inf"):
			fftout.write(str(-150.0) + " ")
		else:
			fftout.write(str(dbfsbins[b+1]) + " ")
	fftout.write('\n')
#END OF MAIN LOOP
end = time.time()
print("Done with analysis")
print("wow, that only took " + str(int(end-start)) + " seconds!")

print("creating header file...")
headerfile = open("songinfo.h",'w')
headerfile.write("const int lines = " + str(numpasses) + ";")
headerfile.write("const int duration = " + str(songduration) + ";")
headerfile.write("const char filename[] = \"" + str(datafilename) + "\";")
headerfile.close()
print("compiling header file...")
os.system("g++ testSky.cpp -o testSky -framework GLUT -framework OpenGL -framework Cocoa")

print("creating audio.c...")
audiofile = open("audio.c",'w')
audiofile.write("#include <stdlib.h> \nint main(int argc, char** argv) {system(\"afplay " + str(fullfilename) + "\");}")
audiofile.close()
print("compiling audio.c...")
os.system("gcc audio.c -o audio")

p1 = subprocess.Popen(["./testSky"])
