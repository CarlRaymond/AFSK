from nrziaudio import *

wf = NrziAudio('leader.wav', 300)

for x in xrange(250):
	wf.writeByte(0x7E)

wf.close()
