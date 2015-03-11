'''
Generates a .wav file encoding data using Bell 202 modem tones (1200Hz and 2200Hz) using NRZI encoding.
'''
import math
import struct
import wave

class NrziAudio:
	MARK_HZ = 2200
	SPACE_HZ = 1200


	SAMPLE_RATE = 44100

	def __init__(self, filename, bitsPerSecond):
		self.filename = filename
		self.bitsPerSecond = bitsPerSecond
		self._lastbit = 0
		self._prepareAudio()
		self._prepareFile()

	def _prepareAudio(self):
		samplesPerBit = NrziAudio.SAMPLE_RATE / self.bitsPerSecond	

		# Generate one bitsworth of mark tone and space tone
		markRadPerSecond = NrziAudio.MARK_HZ * 2 * math.pi
		markSamples = self._sineData(samplesPerBit, markRadPerSecond / NrziAudio.SAMPLE_RATE)
		self._markData = ''.join(markSamples)

		SpaceRadPerSecond = NrziAudio.SPACE_HZ * 2 * math.pi
		spaceSamples = self._sineData(samplesPerBit, SpaceRadPerSecond / NrziAudio.SAMPLE_RATE)
		self._spaceData = ''.join(spaceSamples)



	def _sineData(self, samples, phasePerSample):
		phase = 0.0
		data = []
		for x in xrange(samples):
			value = int( math.sin(phase) * 32767)
			packed = struct.pack('<h', value)
			data.append(packed)
			phase += phasePerSample
		return data

	def _prepareFile(self):
		f = wave.open(self.filename, 'w');
		f.setnchannels(1)
		f.setsampwidth(2)
		f.setframerate(NrziAudio.SAMPLE_RATE)
		f.setcomptype('NONE', 'not compressed')
		self._wavfile = f
	
	def _writeBit(self, bit):
		# NRZI: 0 data bit means flip lastbit.
		if bit == 0:
			self._lastbit ^= 0x01

		if self._lastbit:
			print "M",
			self._wavfile.writeframes(self._markData)
		else:
			print "S",
			self._wavfile.writeframes(self._spaceData)

	def writeByte(self, byte):
		for x in xrange(8):
			bit = byte & 0x01
			self._writeBit(bit)
			byte >>= 1

	def writeInt(self, int):
		for x in xrange(16):
			bit = int & 0x01
			self._writeBit(bit)
			int >>= 1

	def _writeData(self, data):
		self._wavfile.writeframes(data)

	def close(self):
		if self._wavfile:
			self._wavfile.close()
			self._wavfile = None

	def __del__(self):
		self.close()

