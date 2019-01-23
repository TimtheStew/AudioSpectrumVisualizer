
#VizWiz - Frequency Spectrum Analyzer


A fast fourier transform based Frequency Spectrum Analyzer that displays the
amplitude of the frequency spectrum (~40hz - ~24Khz) of an audio file in DBFS.

This directory contains a folder “OSX” which contains release source for OS X
and a folder “Ubuntu” which has release source for ubuntu. It also contains a
folder “older builds” containing mostly junk, but I guess proof that even
though our source is relatively small now, we’ve gone through a lot of code to
get here. It also contains a folder called “wavs” which includes some public
domain music, and folder called "sinetones" which has some single Frequency
wav files, labeled accordingly, and a file "IncFreqDecDBFS.wav" which is the
sine tones concatenated from lowest to highest frequency. (you won't be able
to hear maybe half of them)

##USAGE: python3 vizwiz.py
	NOTES!:
		- hit ESC to exit animation!
		- only takes .wav files!
		- .wav filenames cannot have spaces!
		- see below for more

##DEPENDENCIES: openGL, GLUT, g++, gcc, python3, numpy, tkinter
	openGL:
		- OS X already has development files for OpenGL, to access them we use
		compiler flag -framework openGL
		- Ubuntu also already supports it, to access them we use compiler flags
				-lGL -lGLU
	GLUT:
		- OS X already has development files for GLUT, to access them we use
		compiler flag -framework GLUT
		- Ubuntu also already supports it, to access them we use compiler flag
				-lglut
	g++ & gcc:
		- OS X already has g++ and gcc, our opengl program is written in c++ and our
		audio program in c. we could compile both with g++, but why when we don't
		have to?
	python3:
	  - OS X comes with python2, but I do not believe it comes with python3.
		python3 can be installed along with the next dependency via installation of
		a program like Anaconda
		- Ubuntu probably comes with python3, if not see DIRECTIONS > Installation
		below
	numpy:
		-It is what we are using for the fft itself, and efficient array handling.
	  - OS X does not come with numpy, but it is not hard to install with pip or
		the like.
		- Ubuntu: easy to install if you don't have it see below
	tkinter:
		- We use this for the file selection gui, the entry point to the program.
		- OSX also very easy to install with pip. If you have a newer version of
		python, you probably already have it.
		- Ubuntu: easy to install if you don't have it see below
	sox: (ubuntu only)
		- "swiss army knife of audio" - you probably already have it, if not
					apt-get install sox

##DIRECTIONS:
	###Execution details:
		- There is one entry point to the program, the python file 'vizwiz.py'. It
		can be ran from terminal with 'python3 vizwiz.py', call it as 'python3
		vizwiz.py dev' to get error reporting. (you may see a pipe error if you do
		this, as well as many deprecated warnings, see known bugs section below)

		The program will create a tkinter gui that displays the currently chosen
		filename as well as some metadata about the file. From here you can click
		the 'Choose an Input File' button to select a .wav file for input. Then
		click the "Play" button to begin displaying the animation and playing the
		audio.

	###Acquiring Dependencies:

		OSX------------------OSX---------------------OSX-------------------OSX------
		- The easiest way would probably be to enter the following commands in the
		terminal:

		"curl https://bootstrap.pypa.io/ez_setup.py -o - | sudo python"
			-install easy_install (you probably already have it)

		"sudo easy_install pip"
			-use easy install to get pip

		"pip install numpy"
			-use pip to get numpy

		"pip install tkinter"
			-use pip to get tkinter (you probably already have it)

		This should work, though I cannot test it as I do not have another machine
		which does not already have all of this installed, and I have kind of a
		complicated python set up going, and I'm not trying to uninstall it all and
		start over. If all else fails just install xcode, then homebrew, then
		virtual env and then install numpy and tkinter. (that's what I'm using)
		OSX------------------OSX---------------------OSX-------------------OSX------

		UBUNTU--------------UBUNTU-------------------UBUNTU-------------UBUNTU------
		"sudo apt-get install python3.6"
			-install python3

		"sudo apt-get install python3-tk"
			-install tkinter

		"sudo apt-get install python3-numpy"
			-install numpy
		UBUNTU--------------UBUNTU-------------------UBUNTU-------------UBUNTU------


##FFT Program Operation Description:
	###The Fast Fourier Transform in General:
		- The fft is an O(nlogn) time complexity algorithm for computing the discrete
		Fourier transform (the discrete analog of the continous Fourier Transform)
		which utilizes the the collapsing nature of the roots of unity to divide
		and conquer what is essentially a matrix multiplication. Numpy's fft (which
		we are using, uses Cooley-Turkey with butterflies).

		The fft transforms a signal in the time domain into a signal in the
		frequency domain, we are doing a 1024 pt fft, which means our output will be
		half the size (as we're only using real components for input, our output
		would be 1024 bins mirrored in the middle around the Nyquist frequency
		(samplerate of the file/2)) This is fine as the human audible range is
		only 20Hz-20kHz and wav files are encoded at 41.5kHz-48kHz

    ###Getting the samples:
		- we use the python standard library module wave to read the metadata and
		samples from the .wav files

	###Dealing with channels:
		- if the file only has one channel, we simply pass it along to the next step.
		But if it has two channels, we can add them pre-fft (which due to the
		linearity of the Fourier transform is the same as adding them after, just
		with much less fft computation)

	###High Pass Filtering:
		- Because of how the fft is defined, the value in output bin 0 will be the
		average frequncy of the entire signal. To avoid this data from "corrupting"
		our output, (by artificially increasing values closer to 0) what we want to
		do is subtract from the entire signal (prefft) the value of that 0th bin.
		In order to do this, we fft the signal once, then set the 0th bin of the
		output of that fft to 0, then perform an inverse fft on that data,
		reproducing the original signal but without the "DC component".

		This can also be done (and is perhaps more intuitive) by averaging the time
		domain data per sample, and subtracting that amount from each value in the
		sample, and while that did work, the effects are more prominent with the
		fft->ifft>fft method (at least in our experience)

	###Windowing:
		- The fourier transform, being something which decomposes data into it's
		periodic elements, assumes that the input it's being given is periodic. This
		can present a problem if the shape of the input curve (the measure of
		voltage across the membrane of a microphone) does not have a period of
		exactly 1024. As you can imagine that sort of thing doesn't happen often
		(unless you specifically generate a sine tone for it). So to solve that
		problem we use a window function, there are several at our disposal, but
		currently we are using the Hanning, as it has good side lobe reduction, and
		we are not overly concerned with minor peak spreading.

		A window function is basically a curve that "windows" our input (makes it
		0 valued everywhere outside of the input, and squishes down the sides so
		they approach 0 at the beginning and end of the interval)

		For example, using no window function is equivalent to using a window that
		is 0 everywhere except the sample (0-1024). This is sometimes also called
		the uniform window.

		We apply the window by multiplying our high pass filtered signal with it,
		term by term.

	###The "Actual" FFT:
		- Now that our data is prepared, we fft it to decompose our time chunk into
		a frequency chunk. What we get out is a 512 array of complex numbers. At
		this point we take the magnitudes of those vectors in the complex plane,
		which give us our frequency bin amplitudes on a scale of the width of the
		original samples (in our case 16 bit).

	###Adjusting for Windowing:
		- Windowing may magically fix our discontinuity problem,but it generates
		several of it's own. We did, after all, transform our data quite heavily.
		What we did is reduce the "gain" of the signal, and the amount of gain we've
		lost is equal to the average value of the terms of the window. Looking at
		the definition of the elements of the Hanning window:

				Hanning(n) = 1/2 - 1/2 * cos(n2pi/(N-1)), where N = window size

		It's easy to see, as cos moves between -1 and 1, that the average value of
		those terms is going to be 1/2. So in order to remove that we multiply by
		the reciprocal, 2.*

		*note: this is kind of an oversimplification in ways I don't yet fully
		understand. see TODO/WISHLIST > Multiple Overlapped FFT's section below.

	###Converting to DBFS:
		- To convert to DBFS, we scale the amplitudes back by dividing them by our
		dbfsref constant (32768, the max value on our scale) and then take
		20log_10() of that in order to end up with


##Display Program Operation Description:
	###About OpenGL and GLUT/freeGLUT:
		-On OS X, without homebrew, it's very tricky to install freeGLUT, because of
		this. Luckily OS X comes with regular GLUT, but its old at this point, as
		some licensing nonsense, its outdated. So you may see some deprecated
		errors when compiling (hopefully not, unless you've passed dev). Also, in
		regular GLUT there is no way to gracefully exit the main loop, which is why
		we have pipe troubles (see known bugs section)

	###Creating Vertices:
		-We draw the squares by defining a small unit in both the x and y directions
		which is the size of the gap between the cells. (like 1/16 of 1/64 of the
		screen) Then the cells are just the remaining proportion of the larger
		fraction of the cell. (14/16 of 1/64, each way)

	###Defining Colors:
		- We're using RGB floats, as they're valued from 0 to 1 we create each rows
		color as a slight variation on the previous. Both this and the vertex
		definition step are done ahead of entering the render loop.

	###Audio:
		- to avoid more dependencies we're using command line utilities to play the
		audio. On mac we use "afplay" and on ubuntu we use the "play" command from
		sox, we fork the process that runs it right before entering the mainloop

	###Callback Functions:
		- We set up callback function, to tell the openGL context (basically a giant
		state machine), what to do when certain things happen, for example a key
		press (which we use to check if 'escape' has been hit) but also for things
		like rendering and displaying, and the process that runs when there are no
		events to process

	###Mainloop:
		- The main loop (through various callback functions) calls in whatever order
		it can to update the buffer index, and render the squares by cycling over
		both the array of vertices and colors and turning each cell "on" or "off" by
		setting it to gray or it's color array value.

##GUI Operation Description:
	- It's an OOP tkinter GUI.It is very simple and tkinter is well documented. I
	won't go into too much detail about it here. It uses buttons with lamda
	callback function to register events, and updates it's state accordingly.

	- When you have selected your desired .wav file, the play button will create
	a header file for the display and audio processes and compile them using the
	Makefile provided. (I know this is not "the ideal way" to do this, but
	while global constants may be bad form, they are fast. Believe you me its
	on the TODO)

	- Then the program will create subprocesses for the fft and display processes.
	It pipes the stdout of the fft process to the stdin of the display process
	so we can use that to transfer the data as it is produced before the display
	process reads it into the buffer. The display process waits for a short
	length of time (3-9 seconds usually, depends on length of song) to give the
	fft process a small head start.


##KNOWN BUGS:
	###Spaces in .wav Filenames:
		- as noted above, the wav files cannot contain spaces. I'm pretty sure that
		its to do with how we are playing back the audio (using a command line
		utility native to OS X) and we would need to perform string manipulations on
		the filename in order for it to be executed correctly. This would not be
		that hard to do, but we've never gotten around to it.

	###Anomalous blip around 18 Khz:
	 - something you may notice, if you play several songs, is a small peak
	 around 18 Khz (3/4 across the screen). I have no idea about this one, I think
	 honestly it may be present in the data but I have yet to confirm against an
	 outside source

	###Pipe error:
		- because of how the program exits, sometimes it produces a SIGPIPE error
		(errno 32). Even thought it is expected, caught and handled, python still
		prints it to stderr as being ignored as it considers it an "unusual event",
		there is no way to turn this off, so we've resulted to more primitive means.

	###GUI filedialog glitch:
		- if you hit the exit button the GUI before the filedialog has fully opened
		(click it while it is opening, it is kind of hard to do if your computer
		isn;t slow) then it crashes instead of exiting gracefully. Unsure why,
		might be beyond our control.

##TODO/WISHLIST:
	###Multiple Overlapped FFT's:
		- this would help with our time resolution, as well as let us do more
		precise windowing with asymmetric windows (as long as their overlaps sum
		to a constant over a window length).

	###Units:
		-It would be really great it we could display the frequency values below
		the bins and the DBFS level up the side, especially because it would
		allow verification of data without directly reading the values int the
		file

	###OpenGL 3/4 SDL:
		- this was the original dream, and still something I'd really like to do.
		definitely beyond the scope of this project (or at least beyond the scope
		of us in the timeframe of this project) While I am a little disheartened
		that we couldn't use something more up to date, I still think we made a
		really cool thing, that I'm excited to keep working on in the future. And
		even if we don't move into the core profile of OpenGL we could probably
		switch from GLUT to SDL for a little more control and

	###More Options in GUI:
		- I'd like for overlap percentage, window type, and color parameters to
		be selectable from the GUI

	###Port to using FFTW instead of Numpy:
		- Now that we're much more familiar with fourier analysis and digital
		signal processing, I feel I could effectively wield a tool like fftw,
		which I was not sure of when we started this project.

	###Clean up inter process communication and global variable dependencies
