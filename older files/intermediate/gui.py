from tkinter import *
from tkinter import filedialog
import subprocess
import ntpath

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

root = Tk()
root.filename = filedialog.askopenfilename(initialdir = "./",
											title = "Select .WAV file",
											filetypes=(("WAV files", "*.wav"),("all files","*.*")))

fullfilename = str(root.filename)
root.destroy()
print("launching fft process....")
fftproc = subprocess.Popen(["python3","wavfft2dbfs.py",fullfilename])
