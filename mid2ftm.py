from mido import *
from mido import MidiFile
import sys

path_in = sys.argv[1]
path_out = sys.argv[2]

midi_in = MidiFile(path_in)

ROW_HIGHLIGHT_1 = 4
ROW_HIGHLIGHT_2 = 20

# Writing a blank .ftm for now
ftm_out = open(path_out, "wb")
ftm_out.write("FamiTracker Module".encode("ascii"))
ftm_out.write(b"\x40\x04\x00\x00") # Version number (0.4.3+)

ftm_out.write("PARAMS".encode("ascii")) # Param block title
ftm_out.write(b"\x00" * 10)
ftm_out.write(b"\x06\x00\x00\x00") # Param block version (6)
ftm_out.write(b"\x1d\x00\x00\x00") # Param block size
ftm_out.write(b"\x00")             # Expansion chips disabled
ftm_out.write(b"\x05\x00\x00\x00") # Number of channels (2a03 = 5ch)
ftm_out.write(b"\x00\x00\x00\x00") # PAL mode disabled
ftm_out.write(b"\x00\x00\x00\x00") # Default engine speed
ftm_out.write(b"\x01\x00\x00\x00") # New vibrato mode enabled

ftm_out.write((ROW_HIGHLIGHT_1).to_bytes(4, byteorder='little', signed=False))
ftm_out.write((ROW_HIGHLIGHT_2).to_bytes(4, byteorder='little', signed=False))

ftm_out.write(b"\x20\x00\x00\x00") # Speed/tempo split
