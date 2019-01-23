import wave
import sys
import numpy as np
from array import array
import math

#open the audio file
if len(sys.argv) != 4:
    print("Error - Usage python getwavdata.py <inputfilename.wav> <sampleoutfile> <fftoutfile>")
    sys.exit(2)

#get the wave object
input = wave.open(sys.argv[1],'r')
#and all the baggage
params = input.getparams()
numframes=params.nframes
samplerate=params.framerate
samplewidth=params.sampwidth
numchannels=params.nchannels
samplesize = 1024
numpasses = numframes//samplesize
length = numframes//samplerate
aframespersecond = 30
numaframes = aframespersecond*length
#open the files we'll need
sampleout = open(sys.argv[2],'w')
fftout = open(sys.argv[3],'w')
maxout = open("maxframedata.txt",'w')

#the first 3 lines of both output files are the sample rate, num of frames,
#and then the number of channels
sampleout.write(str(samplerate)+'\n')
sampleout.write(str(numframes)+'\n')
sampleout.write(str(numchannels)+'\n')
fftout.write(str(samplerate)+'\n')
fftout.write(str(numframes)+'\n')
fftout.write(str(numchannels)+'\n')

maxarray = array('f',(0,)*numpasses)
#this will use almost all the samples, though it may leave at worse 1023 unread
#at (usually) less than 1/40th of a second, 1023 frames aint no thang
for passnum in range(numpasses):# + (numframes%samplesize)):
    buffer = array('h')
    #read 1024 frames from input buffer
    #buffer.frombytes(input.readframes(2))
    buffer.frombytes(input.readframes(samplesize))
    #write sample data
    for j in range(0,samplesize-1,numchannels):
        sampleout.write(str(buffer[j])+' ')
        #sampleout.write(str(buffer[j+1])+'\n')
    #perform fft on samples
    signal = np.array(buffer, dtype=float)
    #compute magnitude and write data to file
    fourier = np.fft.rfft(signal)
    re = fourier.real
    im = fourier.imag
    freq = np.fft.rfftfreq(samplesize, d = 1./samplerate)
    fftout.write(str(passnum)+'\n')
    max = 0
    maxf = 0
    for k in range(0,(samplesize//2)):
        mag = math.sqrt(re[k]*re[k] + im[k]*im[k])
        if mag > max:
            max = mag
            maxf = freq[k]

    maxout.write(str(maxf)+'\n')
    maxarray[passnum] = maxf
