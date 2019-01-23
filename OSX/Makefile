all: audio display

audio: audio.c
	@gcc -o audio audio.c

display: liveSky.cpp
	@g++ liveSky.cpp -o liveSky -framework GLUT -framework OpenGL -framework Cocoa
