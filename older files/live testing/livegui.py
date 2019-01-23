from tkinter import *
from tkinter import filedialog
import wave
import subprocess
import ntpath
import os

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)
#create gui window
root = Tk()
#create file filedialog
root.filename = filedialog.askopenfilename(initialdir = "./",
											title = "Select .WAV file",
											filetypes=(("WAV files", "*.wav"),("all files","*.*")))
#save the filename
fullfilename = str(root.filename)
#close gui window
root.destroy()
#get the datafilename to be put in songinfo.h
datafilename = path_leaf(fullfilename) + "fftdata.txt"
#open the wave file to check metadata
input = wave.open(fullfilename,'r')
params = input.getparams()
#number of samples in the file
numframes=params.nframes
#sample rate of the file
samplerate=params.framerate
#number of freqency frames we'll generate
samplesize = 1024
numpasses = numframes//samplesize
#duration of the song (in seconds)
songduration = params.nframes // samplerate

#create songinfo.h
print("creating header file...")
headerfile = open("songinfo.h",'w')
headerfile.write("const int lines = " + str(numpasses) + ";")
headerfile.write("const int duration = " + str(songduration) + ";")
headerfile.write("const char filename[] = \"" + str(datafilename) + "\";")
headerfile.close()
#compile the animation
print("compiling header file...")
os.system("g++ liveSky.cpp -o liveSky -framework GLUT -framework OpenGL -framework Cocoa")

#create audio.c
print("creating audio.c...")
audiofile = open("audio.c",'w')
audiofile.write("#include <stdlib.h> \nint main(int argc, char** argv) {system(\"afplay " + str(fullfilename) + "\");}")
audiofile.close()
#compile audio.c
print("compiling audio.c...")
os.system("gcc audio.c -o audio")

#launch the fft and display processes
print("launching fft process....")
fftproc = subprocess.Popen(["python3","livewavfft2dbfs.py",fullfilename], stdout=subprocess.PIPE)
print("launching display process....")
displayproc = subprocess.Popen(["./liveSky", fullfilename],stdin=fftproc.stdout, stdout=subprocess.PIPE)
#fftproc.stdout.close()
#communicate() is like wait()
outs, errs = displayproc.communicate()
print(outs)
print(errs)
