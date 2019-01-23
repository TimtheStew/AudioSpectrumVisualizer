#create a dialog that lets people choose an input file
from tkinter import filedialog
from tkinter import *
import wave
import sys
import numpy as np
from array import array
import math

root = Tk()
root.filename = filedialog.askopenfilename(initialdir = "./",
                                            title = "Select .WAV file",
                                            filetypes=(("WAV files", "*.wav"),("all files","*.*")))
print(root.filename)

#open that file and analyze it, creating frame by frame frequency data

#get the wave object
dumpsamples = False
input = wave.open(root.filename,'r')
#and all the baggage
params = input.getparams()
numframes=params.nframes
samplerate=params.framerate
samplewidth=params.sampwidth
numchannels=params.nchannels
#we're doing a 1024 pt fft
samplesize = 1024
#number of frequency bins for output
numbins = 32
samplesperbin = ((samplesize//2)//numbins)
#the number of fft passes we'll make on the samples
numpasses = numframes//samplesize
#duration of the song (in seconds)
songduration = params.nframes // samplerate

#open the files we'll need
if dumpsamples:
    sampleout = open("sampledump.txt",'w')
fftout = open("fftdata.txt",'w')

#the first 3 lines of the sample file are the sample rate, num of frames,
#and then the number of channels
if dumpsamples:
    sampleout.write(str(samplerate)+'\n')
    sampleout.write(str(numframes)+'\n')
    sampleout.write(str(numchannels)+'\n')
#first line of fft data file is the duration of the song in seconds
fftout.write(str(songduration) +'\n')
#second line of fft data file is the num of passes (lines of data in the file)
fftout.write(str(numpasses)+'\n')
#the third line is the number of bins (values on each line, seperated by spaces)
fftout.write(str(numbins)+'\n')

#this will use almost all the samples, though it may leave at worse 1023 unread
#at (usually) less than 1/40th of a second, 1023 frames aint no thang
for passnum in range(numpasses):# + (numframes%samplesize)):
    rawbuffer = array('h')
    #read 1024 frames from input buffer
    rawbuffer.frombytes(input.readframes(samplesize))
    #write sample data
    if dumpsamples:
        for j in range(0,numchannels*samplesize-1,numchannels):
            for i in range(numchannels):
                sampleout.write(str(rawbuffer[j+i])+' ')
                #sampleout.write(str(buffer[j+1])+'\n')
            sampleout.write('\n')
    #get the frequency index values
    #freq = np.fft.rfftfreq(samplesize, d = 1./samplerate)
    #If there are multiple channels we split the samples.
    #first we convert to numpy arrays (we'll need to later anyway)
    rawchannels = np.array(rawbuffer, dtype=float)
    signals = np.zeros((numchannels, samplesize))
    for j in range(samplesize):
        for i in range(numchannels):
            signals[i][j] = rawchannels[i+j]
    #perform fft on samples
    fourier = np.zeros((numchannels, samplesize//2+1))
    for channel in range(numchannels):
        signal = signals[channel]
        fourier[channel] = np.fft.rfft(signal)
    #get the real and imaginary components
    #each is an array of size (numchannels, samplesize)
    re = fourier.real
    im = fourier.imag
    #compute the magnitude and write sums to bins
    #fftout.write(str(passnum)+'\n')
    bins = np.zeros((numchannels,numbins))
    #loop over channels
    for c in range(numchannels):
        #loop in bin sized chunks over frequencies
        currbin = 0
        for b in range(0,(samplesize//2),samplesperbin):
            sigma = 0.0
            #loop through a bin's worth of samples
            for s in range(samplesperbin):
                #compute the magnitudes and sum
                mag = math.sqrt(re[c][b+s]*re[c][b+s] + im[c][b+s]*im[c][b+s])
                #print(str(mag))
                sigma = sigma + mag
                #print(str(sigma)+' ')
            #print('\n')
            #save the sums in the bins
            bins[c][currbin] = sigma
            currbin = currbin + 1
    #average the channels down to one set of bins
    #it uses the first row of bins[][] b/c it'll exist w/ only 1 channel
    for b in range(numbins):
        sigma = 0.0
        for c in range(numchannels):
            sigma = sigma + bins[c][b]
        bins[0][b] = (sigma/numchannels)
    #normalize the bins
    #write the bins to the files
    m = bins[0].max()/100
    for b in range(numbins):
        fftout.write(str(bins[0][b] / m ) + " ")
    fftout.write('\n')
