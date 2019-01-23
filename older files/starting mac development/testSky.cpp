
#include <unistd.h>
#include <math.h>
#include <stdlib.h>
#include <iostream>
#include <fstream>
#include <GL/freeglut.h>  // GLUT, include glu.h and gl.h
#include <stdio.h>
#include <signal.h>
#include "songinfo.h"

// GLOBAL VARIABLES/CONSTANTS
const int rows = 32;
const int cols = 512;
//const int lines = 10499;
//const char filename[] = "spiritfftdata.txt";
//const int duration = 243;
const float indicesPerSecond = lines/duration;

GLfloat verts[rows*cols][4][2];
GLfloat colors[rows][3];
GLfloat nowCols[cols];
GLfloat buff[lines][cols];

void display();

void createVertices(){
    GLfloat dy = (1.0/(rows/2.0))/16.0;
    GLfloat dx = (1.0/(cols/2))/16.0;
    GLfloat yside = 14 * dy;
    GLfloat xside = 14 * dx;


    for (int i = 0; i < cols; i++) {
        for (int j = 0; j < rows; j++){

            GLfloat x = -1 + dx + (xside+2*dx)*i;
            GLfloat y = -1 + dy + (yside+2*dy)*j;
            //bottom left
            verts[rows*i + j][0][0] = x;
            verts[rows*i + j][0][1] = y;
            //bottom right
            verts[rows*i + j][1][0] = x + xside;
            verts[rows*i + j][1][1] = y;
            //upper right
            verts[rows*i + j][2][0] = x + xside;
            verts[rows*i + j][2][1] = y + yside;
            //upper left
            verts[rows*i + j][3][0] = x;
            verts[rows*i + j][3][1] = y + yside;
        }
    }
}

//      Define colors
void defineColors() {
    GLfloat r,g,b,dc,dg,dr,db;
    int i;
    dc = 1.0/256.0f;

    //first
    r = b = 0.0f;
    g = 153.0*dc;
    dg = 101.0/32.0;
    for(i = 0; i < 12; i++){
        colors[i][0] = r;
        colors[i][1] = g + dg*i*dc;
        colors[i][2] = b;
    }

    //second
    b = 0;
    g = 1.0;
    dr = 8.0;
    for (i = 12; i < 20; i++){
        colors[i][0] = dr*(i-32)*dc;
        colors[i][1] = 1.0;
        colors[i][2] = b;
    }

    //third
    r = 1.0;
    dg = dr;
    for (i = 20; i < rows; i++){
        colors[i][0] = 1.0f;
        colors[i][1] = 1.0f - dc*dg*(i-64);
        colors[i][2] = 0.0f;
    }
}

/* Initialize OpenGL Graphics */
void initGL() {
    // Set "clearing" or background color
    glClearColor(0.0f, 0.0f, 0.0f, 1.0f); // Black and opaque
    createVertices();
}

//IDLE
void onIdle(){

    int ind;
    float time = glutGet(GLUT_ELAPSED_TIME)/1000.0;
    // Song is done
    if (time > duration){
        exit(1);
	}
    ind = (int)(time * indicesPerSecond);


    //printf("INdex: %d\n", ind);
    for (int i = 0; i < cols; i++){
      nowCols[i] = buff[ind][i];
    }

    display();
}


/* Handler for window-repaint event. Call back when the window first appears and
   whenever the window needs to be re-painted. */
void display() {
    glClear(GL_COLOR_BUFFER_BIT);   // Clear the color buffer with current clearing color

    float dbperbox = 135/rows;
    int ind;
    for(int i = cols-1; i >= 0; i--){
        for(int j = 0; j < rows; j++){

            glBegin(GL_QUADS);
            if (nowCols[i] > (j-rows)*dbperbox){
				glColor3f(colors[j][0],colors[j][1],colors[j][2]);
            }
            else {
				glColor3f(0.1f,0.1f,0.1f);
            }
            glVertex2f(verts[(rows*i) +j][0][0], verts[(rows*i) + j][0][1]);
            glVertex2f(verts[(rows*i) +j][1][0], verts[(rows*i) + j][1][1]);
            glVertex2f(verts[(rows*i) +j][2][0], verts[(rows*i) + j][2][1]);
            glVertex2f(verts[(rows*i) +j][3][0], verts[(rows*i) + j][3][1]);

            glEnd();  // Render now
        }
    }
    glutSwapBuffers();
}

// Read frequency data from file into buffer -- needs work
void readFFT(){

    std::ifstream inFile;
    inFile.open(filename);
    if(!inFile.is_open()){
        exit(1);
    }
    int dump = 0;
    inFile >> dump;
    inFile >> dump;
    inFile >> dump;
    for (int x = 0; x < lines; x++){
        for(int y = 0; y < cols; y++){
            inFile >> buff[x][y];
        }
    }
    inFile.close();
}
/* Main function: GLUT runs as a console application starting at main()  */
int main(int argc, char** argv) {

    readFFT();

    pid_t pid;
    pid = fork();               // Fork.
    if(pid<0){
      printf("fork failed \n");
      return 1;
    }
    //char *lol[1];
    //lol[0] = "c";
    if(pid == 0){
        execv("audio", argv );     //executes program that plays song
    }


    else{
        defineColors();
        glutInit(&argc, argv);          // Initialize GLUT
        glutCreateWindow("lmao");  // Create window with the given title
        glutInitWindowSize(720, 640);   // Set the window's initial width & height
        glutInitWindowPosition(50, 50); // Position the window's initial top-left corner
        glutDisplayFunc(display);       // Register callback handler for window re-paint event
        initGL();                       // Our own OpenGL initialization
        glEnable(GL_BLEND);
        glutIdleFunc(onIdle);
        glutMainLoop();                 // Enter the event-processing loop
        wait(NULL);
        return 0;
    }
}
