import nrziaudio

wf = NrziAudio('test.wav', 2)

wf.writeByte(0x7E)

wf.close()
