#import sys

#print("proc 1 says the filename is: " + str(sys.argv[1]))

message = ["hello","this","is","my","message"]

print(str(len(message)))

for word in message:
    print(word + " ")
