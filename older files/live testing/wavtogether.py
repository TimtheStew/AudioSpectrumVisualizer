import wave
import sys
from array import array

output = wave.open("incFreq_decDBFS.wav",'w')
output.setnchannels(1)
output.setframerate(48000)

buff = array('h')
freq1 = wave.open("40Hz0dBFS.wav")
p1 = freq1.getparams()
buff.frombytes(p1.readframes(p1.nframes))
output.writeframes(buff)
output.close()
freq1.close()
# freq2 = wave.open("93Hz-3dBFS.wav")
# freq3 = wave.open("100Hz-3dBFS.wav")
# freq4 = wave.open("500Hz-5dBFS.wav")
# freq5 = wave.open("1000Hz-10dBFS.wav")
# freq6 = wave.open("5000Hz-15dBFS.wav")
# freq7 = wave.open("10000Hz-25dBFS.wav")
# freq8 = wave.open("12000Hz_-30dBFS.wav")
# freq9 = wave.open("16000Hz-40dBFS.wav")
# freq9 = wave.open("20000Hz-55dBFS.wav")
# freq9 = wave.open("23500Hz_-70dBFS.wav")
