'''
Generates a .wav file with 60 seconds of HDLC flag byte (0x7E) using Bell 202 NRZI encoding at 1200 bps.
'''

import math;
import struct;
import wave;

SAMPLES_PER_BIT = SAMPLE_RATE / BITRATE;

signal = wave.open('flag.wav'.format(FREQ_HZ), 'w');
signal.setnchannels(1);
signal.setsampwidth(2);
signal.setframerate(SAMPLE_RATE);
signal.setcomptype('NONE', 'not compressed');

