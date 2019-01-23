import subprocess
import time
#create two new processes, and pipe the stdout of p1 to stdin of p2
p1 = subprocess.Popen(["python3","proc1.py"], stdout=subprocess.PIPE)
p2 = subprocess.Popen(["./proc2"], stdin=p1.stdout, stdout=subprocess.PIPE)
p1.stdout.close()

#this is wait() more or less
outs,errs = p2.communicate()
print(outs)
p1.kill()
