#include <stdio.h>
#include <unistd.h>
#include <math.h>
#include <stdlib.h>
#include <iostream>
#include <fstream>
#include <GL/freeglut.h>  // GLUT, include glu.h and gl.h
#include <stdio.h>
#include <signal.h>
#include <thread>
#include "songinfo.h"

// GLOBAL VARIABLES/CONSTANTS
const int rows = 96;
const int cols = 512;
const float indicesPerSecond = lines/duration;

GLfloat verts[rows*cols][4][2];
GLfloat colors[rows][3];
GLfloat nowCols[cols];
GLfloat buff[lines][cols];

pid_t audiopid;

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
  r = g = 0;
  b = 153.0*dc;
  dg = (153.0/24.0)*dc;
  for(i = 0; i < rows/4; i++){
      colors[i][0] = 0.0f;
      colors[i][1] = 0.0f + dg*i;
      colors[i][2] = b;
  }

  //second
  r = 0;
  b = g = (153.0)*dc;
  db = dg;
  for(i = rows/4; i < rows/2; i++){
      colors[i][0] = r;
      colors[i][1] = g;
      colors[i][2] = b - (i - 24)*db;
  }

  //third
  r = b = 0;
  g = (153.0)*dc;
  dr = db = dg;
  for(i = rows/2; i < 3*(rows/4); i++){
      colors[i][0] = r + (i - 48)*dr;
      colors[i][1] = g;
      colors[i][2] = b;
  }


  //fourth
  b = 0;
  r = g = (153.0)*dc;
  dr = db = dg;
  for(i = 3*(rows/4); i < rows; i++){
      colors[i][0] = r;
      colors[i][1] = g - (i - 72)*dg;
      colors[i][2] = b;
  }
}

/* Initialize OpenGL Graphics */
void initGL() {
    // Set "clearing" or background color
    glClearColor(0.0f, 0.0f, 0.0f, 1.0f); // Black and opaque
    createVertices();
}
void killaudio(){
  system("killall afplay");
  system("clear");
  return;
}
//IDLE
void onIdle(){

    int ind;
    float time = glutGet(GLUT_ELAPSED_TIME)/1000.0;
    // Song is done
    if (time > duration){
      killaudio();
      exit(0);
	}
    ind = (int)(time * indicesPerSecond);


    //printf("INdex: %d\n", ind);
    for (int i = 0; i < cols; i++){
      nowCols[i] = buff[ind][i];
    }

    display();
}
void processKeys(unsigned char key, int x, int y) {
    if (key == 27){
        killaudio();
        exit(0);
    }
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

void readFFT(){
    GLfloat temp;
    for (int x = 0; x < lines; x++){
        for(int y = 0; y < cols; y++){
            scanf("%f", &temp);
            //printf("%f ",&temp);
            buff[x][y] = temp;
        }
    }
}

/* Main function: GLUT runs as a console application starting at main()  */
int main(int argc, char** argv) {
      std::thread datamonkey(readFFT);
      defineColors();
      sleep(7);
      audiopid = -1;
      audiopid = fork();               // Fork.
      if(audiopid<0){
        printf("fork failed \n");
        return 1;
      }else if(audiopid == 0){
          execv("audio", argv);     //executes program that plays song
      }
      else{
          glutInit(&argc, argv);          // Initialize GLUT
          glutCreateWindow("lmao");  // Create window with the given title
          glutInitWindowSize(720, 640);   // Set the window's initial width & height
          glutInitWindowPosition(50, 50); // Position the window's initial top-left corner
          glutDisplayFunc(display);       // Register callback handler for window re-paint event
          initGL();                       // Our own OpenGL initialization
          glEnable(GL_BLEND);
          glutIdleFunc(onIdle);
          glutKeyboardFunc(processKeys);
          glutMainLoop();                 // Enter the event-processing loop
          killaudio();
          return 0;
      }
    }
//}
