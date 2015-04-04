from nrziaudio import *

wf = NrziAudio('leader-96000.wav', 1200)

for x in xrange(250):
	wf.writeByte(0x7E)

wf.close()
