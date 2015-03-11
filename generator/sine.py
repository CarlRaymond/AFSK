import math;
import struct;
import wave;

SAMPLE_RATE = 44100;
MAX_VALUE = 32767;
CHANNELS = 1;

FREQ_HZ = 2200;
FREQ_RAD = FREQ_HZ * 2 * math.pi;

sinewave = wave.open('sine-{0}.wav'.format(FREQ_HZ), 'w');
sinewave.setnchannels(1);
sinewave.setsampwidth(2);
sinewave.setframerate(SAMPLE_RATE);
sinewave.setcomptype('NONE', 'not compressed');

PHASE_PER_SAMPLE = FREQ_RAD / SAMPLE_RATE;

print "Phase per sample: {0}".format(PHASE_PER_SAMPLE);

# Generate 10 seconds of sine
total_samples = SAMPLE_RATE * 10;
phase = 0;


for sec in xrange(10):
	cycle_values = [];

	for x in xrange(SAMPLE_RATE):
		value = int( math.sin(phase) * 32767 );
		packed = struct.pack('<h', value);
		#print packed,
		cycle_values.append(packed);
		phase += PHASE_PER_SAMPLE;

	value_string = ''.join(cycle_values);
	sinewave.writeframes(value_string);

sinewave.close();