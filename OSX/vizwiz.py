#from tkinter import Tk, Label, Button, StringVar, IntVar, END, W, E, filedialog
from tkinter import *
#from tkinter.ttk import *
from tkinter import filedialog
import os
import subprocess
import ntpath
import wave
import socket
import errno
import sys


class Vizwiz:

	def __init__(self, master):
		self.master = master
		master.title("VizWiz")
		self.samplesize = 1024
		self.numpasses = 0

		self.filename = "no file yet selected"
		self.samprate = 0
		self.duration = 0
		self.windowtype = "Hanning"

		#Filename label
		self.file_label_text = StringVar()
		self.file_label_text.set(self.filename)
		self.file_label = Label(master, textvariable=self.file_label_text)
		self.flabel = Label(master, text="Filename:")
		#samplerate Label
		self.samprate_label_text = IntVar()
		self.samprate_label_text.set(self.samprate)
		self.samprate_label = Label(master, textvariable=self.samprate_label_text)
		self.srlabel = Label(master, text="Samples per Second:")
		#songduration Label
		self.duration_label_text = StringVar()
		self.duration_label_text.set(self.duration)
		self.duration_label = Label(master, textvariable=self.duration_label_text)
		self.dlabel = Label(master, text="Duration in seconds:")

		#windowing choice
		# self.window_choice_text = StringVar()
		# self.window_choices = ["Hanning","Hamming","Blackman","Bartlett","Uniform (none)"]
		# self.window_dropdown = Combobox(master, textvariable=self.window_choice_text, values=self.window_choices)
		# self.window_dropdown.current(0)
		# self.window_dropdown.config(state="readonly")
		# self.window_dropdown.bind("<<ComboboxSelected>>",self.update("window"))
		# self.wlabel = Label(master, text="Windowing:")


		self.choosefile_button = Button(master, text="Choose an Input File", command=lambda: self.update("file"))
		self.play_button = Button(master, text="Play", command=lambda: self.update("play"),state="disabled")


		# LAYOUT
		#filename
		self.flabel.grid(row=0, column=0, sticky=W)
		self.file_label.grid(row=0, column=1, columnspan=2, sticky=E)
		#samplerate
		self.srlabel.grid(row=1, column=0, sticky=W)
		self.samprate_label.grid(row=1, column=1, columnspan=1, sticky=E)
		#duration
		self.dlabel.grid(row=2, column=0, sticky=W)
		self.duration_label.grid(row=2, column=1, columnspan=1, sticky=E)
		#Windowing
		#self.wlabel.grid(row=3, column=0, sticky=W)
		#self.window_dropdown.grid(row=3, column=1, sticky=W)
		#buttons
		self.choosefile_button.grid(row=4, column=0)
		self.play_button.grid(row=4, column=1)
	def create_info_file(self, numpasses, duration, filename):
		self.headerfile = open("songinfo.h",'w')
		self.headerfile.write("const int lines = " + str(numpasses) + ";")
		self.headerfile.write("const int duration = " + str(duration) + ";")
		self.headerfile.write("const char filename[] = \"" + str(filename) + "\";")
		self.headerfile.close()

	def create_audio_file(self, fullfilename):
		self.audiofile = open("audio.c",'w')
		self.audiofile.write("#include <stdlib.h> \nint main(int argc, char** argv) {system(\"afplay " + str(fullfilename) + "\");}")
		self.audiofile.close()

	def path_leaf(self, path):
		head, tail = ntpath.split(path)
		return tail or ntpath.basename(head)

	def update(self, method):
		if method == "file":
			self.fullfilename = filedialog.askopenfilename(initialdir = "./",
													title = "Select .WAV file",
													filetypes=(("WAV files", "*.wav"),("all files","*.*")))
			self.filename = self.path_leaf(self.fullfilename)
			self.input = wave.open(self.fullfilename,'r')
			self.params = self.input.getparams()
			self.samprate = self.params.framerate
			self.numframes = self.params.nframes
			self.duration = self.numframes//self.samprate
			self.numpasses = self.numframes//self.samplesize
			self.play_button.config(state="normal")


		elif method == "play":
			self.play_button.config(state="disabled")
			self.create_info_file(self.numpasses, self.duration, self.filename)
			self.create_audio_file(self.fullfilename)
			# self.headerfile = open("songinfo.h",'w')
			# self.headerfile.write("const int lines = " + str(self.numpasses) + ";")
			# self.headerfile.write("const int duration = " + str(self.duration) + ";")
			# self.headerfile.write("const char filename[] = \"" + str(self.filename) + "\";")
			# self.headerfile.close()
			#os.system("g++ liveSky.cpp -o liveSky -framework GLUT -framework OpenGL -framework Cocoa")
			#os.system("gcc audio.c -o audio")
			makeproc = subprocess.Popen(["make","all"])
			self.out, self.errs = makeproc.communicate()
			#os.system("make all")
			try:
				fftproc = subprocess.Popen(["python3","livewavfft2dbfs.py",self.fullfilename], stdout=subprocess.PIPE)
				displayproc = subprocess.Popen(["./liveSky", self.fullfilename],stdin=fftproc.stdout, stdout=subprocess.PIPE)
				self.outs, self.errs = displayproc.communicate()
			except Exception as e:
				something = e;
			self.play_button.config(state="normal")

		# elif method == "window":
		# 	self.windowtype = self.window_dropdown.get()
		else: # reset
			self.filename = "no file yet selected"

		self.file_label_text.set(self.filename)
		self.samprate_label_text.set(self.samprate)
		self.duration_label_text.set(self.duration)
		# self.window_choice_text.set(self.windowtype)


root = Tk()
my_gui = Vizwiz(root)
if (len(sys.argv) > 1):
	if (sys.argv[1] != "dev"):
		sys.stdout.close()
		sys.stderr.close()
root.mainloop()
