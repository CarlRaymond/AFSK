'''
The modulator is an iterator that generates audio samples of a bitstream.

The demodulator simulates the decoding process in the BeRTOS AFSK decoder
'''

import collections
import math


def __quantize(phase, amplitude):
	val = math.sin(phase) * amplitude
	return int(val)

# Compares lsb and next-to-lsb for differentness
def __edgefound(value):
	twobits = value & 0x3
	return (twobits == 0x01 or twobits == 0x10)

# markfreq: frequency of mark symbol in Hertz
# spacefreq: frequency of space symbol in Hertz
# samplerate: no. of audio samples per second to generate
# bitrate: bit rate to generate
# symbolstream: a generator of data bits to modulate (1 for mark, 0 for space)

def modulator(symbolstream, markfreq=1200, spacefreq=2200, samplerate=9600, bitrate=1200, amplitude = 127):

	phasepermarksample = 2 * math.pi * markfreq / samplerate
	phaseperspacesample = 2 * math.pi * spacefreq / samplerate

	samplesperbit = samplerate / bitrate
	samplebitcount = 0
	phase = 0.0
	dataindex = 0
	lastbit = 0

	# Phase accumulator
	phase = 0.0

	for symbol in symbolstream:

		#print '   bit: {0}'.format(bit)
		if symbol == 0:
			#print 'S'
			phasedelta = phaseperspacesample
		else:
			#print 'M'
			phasedelta = phasepermarksample

		for s in xrange(samplesperbit):
			yield __quantize(phase, amplitude)
			phase += phasedelta


# Simulates the AFSK demodulator on a given sample source. Returned bits are the raw demodulated mark and space
# bits, which will need further processing to un-NRZI them.
def demodulator(modulator):
	samplesperbit = 8

	PHASE_BIT = 8
	PHASE_INC = 1

	PHASE_MAX = (samplesperbit * PHASE_BIT)
	PHASE_THRES = (PHASE_MAX / 2) # - PHASE_BIT / 2)

	currentphase = 0

	fifolen = samplesperbit / 2
	fifo = collections.deque(fifolen * [0], fifolen)

	iir_x = [0, 0]
	iir_y = [0, 0]

	sampledbits = 0

	lastbit = 0
	thisbit = 0

	for sample in modulator:
		delayed = fifo.pop()
		#print "Sample: {0} Delayed: {1}".format(sample, delayed)
		iir_x[0] = iir_x[1]
		#iir_x[1] = int(delayed * sample / 6.027339492)
		iir_x[1] = delayed * sample >> 2

		iir_y[0] = iir_y[1]
		#iir_y[1] = iir_x[0] + iir_x[1] + int(iir_y[0] * 0.6681786379)
		iir_y[1] = iir_x[0] + iir_x[1] + (iir_y[0] >> 1) + (iir_y[0] >> 3) + (iir_y[0] >> 5)


		#print "X: {0}, {1}\t\tY: {2}, {3}".format(iir_x[0], iir_x[1], iir_y[0], iir_y[1])
		sampledbits <<= 1
		sampledbits |= 1 if (iir_y[1] > 0 ) else 0

		# Store the current sample in the fifo
		fifo.appendleft(sample)

		# If there is an edge, adjust phase sampling
		if __edgefound(sampledbits):
			#print "EDGE!"
			if currentphase < PHASE_THRES:
				currentphase += PHASE_INC
			else:
				currentphase -= PHASE_INC
		currentphase += PHASE_BIT
		#print "Current phase: {0}".format(currentphase)

		# Sample the bit
		if currentphase > PHASE_MAX:
			currentphase %= PHASE_MAX

			#
			# Determine bit value by reading the last 3 sampled bits.
			# If the number of ones is two or greater, the bit value is a 1,
			# otherwise is a 0.
			# This algorithm presumes that there are 8 samples per bit.
	 		#
			bits = sampledbits & 0x07
			if bits == 0x07 or bits == 0x06 or bits == 0x05 or bits == 0x03:
				yield 1
			else:
				yield 0


# Accepts an NRZI-encoded bitstream, and produced a plain bitstream.  A bit transition in the input
# becomes a 0 in the output; a non-transition becomes a 1 in the output.
def unNRZ(bitstream):
	lastbit = bitstream.next()

	for currentbit in bitstream:
		yield 1 if currentbit == lastbit else 0
		lastbit = currentbit


# Accepts a plain bitstream, and produces an NRZI bitstream. A 0 bit in the input causes
# a transition in the oubput symbol.
def NRZ(bitstream):
	symbol = 0

	for currentbit in bitstream:
		if currentbit == 0:
			symbol ^= 0x01
		yield symbol


# Generates bits from a bytestream, emitting LSB first
def bitstreamer(bytestream):
	for byte in bytestream:
		for b in xrange(8):
			yield byte & 0x01
			byte >>= 1


# Generates bytes from a bitstream.
def bitunstreamer(bitstream):
	bitcount = 0
	byte = 0
	for bit in bitstream:
		byte >>= 1
		if bit == 1:
			byte |= 0x80
		bitcount += 1
		if bitcount == 8:
			yield byte
			bitcount = 0


def unframer(bitstream):
	states = { idle: 0, flag: 1, data: 10 }
	state = states.idle
	consecutive1s = 0
	currentbyte = 0
	FLAG = 0x7e
	ERROR = 0xfe

	# Bits arrive in LSB order, so shift in from left

	for bit in bitstream:
		if state == states.idle:
			# Looking for a flag byte
			currentbyte >= 1
			if bit == 1:
				currentbyte |= 0x80

			if currentbyte == FLAG:
				state = states.data

		elif state == states.flag:
			# Stay in this state as long as flag seen


		elif state == states.data:
			# Receive bits as long as they aren't too flagy
			for b in xrange(8):
				currentbyte >= 1
				if bit == 1:
					currentbyte |= 0x80
				if currentbyte & 0xfe ==


# Create some data to transmit. ~ corresponds to 0x7e, the HDLC flag byte
sourcedata = bytearray( b'~~~~Whazzup!~~~~')
sourcebits = bitstreamer(sourcedata)
sourcesamples = modulator(NRZ(sourcebits))

filtered = sourcesamples
#filtered = [sample *0.2 for sample in sourcesamples]

receivedbits = unNRZ(demodulator(filtered))
#receiveddata = [byte for byte in bitunstreamer(receivedbits)]

print "Data:    {0}".format(sourcedata)
#print "Decoded: {0}".format(receiveddata)
print "Bits: ",
for bit in receivedbits:
	print bit,
