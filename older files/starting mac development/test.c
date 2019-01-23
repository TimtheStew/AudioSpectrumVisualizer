#include <stdio.h>
#include <math.h>
#include "fftw3.h"

int main(int argc, char *argv[]){
  int input_size = 1024;
  int output_size = (input_size / 2 + 1);

  double* input_buffer = static_cast<double*>(fftw_malloc(input_size * sizeof(double)));
  fftw_complex* output_buffer = static_cast<fftw_complex*>(fftw_malloc(output_size * sizeof(fftw_complex)));

  int flags = FFTW_ESTIMATE;
  fftw_plan plan = fftw_plan_dft_r2c_1d(input_size, input_buffer,
                                            output_buffer, flags);
  FILE *inputfp, *outputfp;
  inputfp = fopen("wavdata.txt", "r");
  outputfp = fopen("fftdata.txt", "w+");

  int num_samples, sample_rate;
  fscanf(inputfp,"%d",&sample_rate);
  fscanf(inputfp,"%d",&num_samples);

  int numloops = (num_samples/input_size) - 1;

  int i,j,k,tempLC, tempRC;
  double temp, re, im, amp;
  for (i = 0; i < numloops; i++){
    fprintf(outputfp,"%dth chunk\n", i);
    fprintf(outputfp, "-------------------------------------------------------\n");
    for (j = 0; j<input_size; j++){
      fscanf(inputfp,"%d", &tempLC);
      fscanf(inputfp,"%d", &tempRC);
      temp = (double) tempLC;
      input_buffer[j]=temp;
    }
    fftw_execute(plan);
    for (k=0;k<output_size;k++){
      re = output_buffer[k][0];
      im = output_buffer[k][1];
      amp = sqrt((re*re)+(im*im));
      fprintf(outputfp, "%dth freq. bin: %lf\n",k,amp);
    }
  }
  fclose(inputfp);
  fclose(outputfp);
  fftw_free(input_buffer);
  fftw_free(output_buffer);
  fftw_destroy_plan(plan);

  return 0;
}
