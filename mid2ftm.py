from mido import *
from mido import MidiFile
import sys

path_in = sys.argv[1]
path_out = sys.argv[2]

midi_in = MidiFile(path_in)

# Writing a blank .ftm for now
ftm_out = open(path_out, "wb")
ftm_out.write("FamiTracker Module".encode("ascii"))
ftm_out.write(b"\x40\x04\x00\x00") # Version number (0.4.3+)
