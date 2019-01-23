#include <stdio.h>

int main(int argc, char** argv){

  printf("\nfilename = %s\n",argv[1]);
  int length;
  scanf("%d", &length);
  printf("length = %d\n",length);
  char str[100];
  int i;
  for(i = 0; i < length; i++){
    scanf("%s",str);
    printf("this is proc2 and i got: %s\n", str);
  }
  return 1;
}
