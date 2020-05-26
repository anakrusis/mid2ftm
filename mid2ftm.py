from mido import *
from mido import MidiFile
import sys
import math

path_in = sys.argv[1]
path_out = sys.argv[2]

midi_in = MidiFile(path_in)
ftm_out = open(path_out, "wb")

patterns = [] # stores all pattern data

ROW_HIGHLIGHT_1 = 4
ROW_HIGHLIGHT_2 = 20

def main():
   
    writeHdrAndParams(ftm_out)

    currentPattern = 0
    patterns.append( newPattern(0,0,currentPattern) )
    currentTime = 0

    track = midi_in.tracks[1]
    print('Track {}: {}'.format(1, track.name))
    for msg in track:
        print(msg)
        if msg.type == 'note_on' and msg.velocity != 0:
            patterns[currentPattern][3] = addToBytes( patterns[currentPattern][3], 4, 1)
            patterns[currentPattern].extend( midiNoteToRow(msg.note, msg.velocity, currentTime) )
            currentTime += 1
            if currentTime >= 64:
                currentPattern += 1
                patterns.append( newPattern(0,0,currentPattern) )
                currentTime = 0;
    

    writeInstruments()
    writeFrames()
    writePatterns()

def writeInstruments():
    ftm_out.write("INSTRUMENTS".encode("ascii")) # Instruments block title
    ftm_out.write(b"\x00" * 5)
    ftm_out.write(b"\x06\x00\x00\x00")     # version 6
    ftm_out.write(b"\x49\x01\x00\x00")     # instrument size 0x0149

    ftm_out.write(b"\x01\x00\x00\x00")     # Number of instruments: 1
    ftm_out.write(b"\x00\x00\x00\x00\x01") # Instrument index 0, 2a03
    ftm_out.write(b"\x05\x00\x00\x00")     # 5 sequences for 2a03
    ftm_out.write(b"\x00\x00\x00\x00\x00" * 2) # None of the 5 sequences are defined

    ftm_out.write(b"\x00\x00\xff" * 96)    # DPCM samples blank for all 96 notes uwu
    ftm_out.write(b"\x0e\x00\x00\x00")     # Instrument name length: 14
    ftm_out.write("New instrument".encode("ascii")) # Instrument name

def writeFrames():
    ftm_out.write("FRAMES".encode("ascii")) # Frames block title
    ftm_out.write(b"\x00" * 10)
    ftm_out.write(b"\x03\x00\x00\x00") # Frames block version (3)
    ftm_out.write( ( 16 + (len(patterns) * 5) ).to_bytes(4, byteorder='little', signed=False) ) # Frames block size

    ftm_out.write(( len(patterns) ).to_bytes(4, byteorder='little', signed=False)) # number of frames
    ftm_out.write((2).to_bytes(4, byteorder='little', signed=False)) # speed
    ftm_out.write((150).to_bytes(4, byteorder='little', signed=False)) # tempo
    ftm_out.write((64).to_bytes(4, byteorder='little', signed=False)) # rows per frame

    for i in range(0, len(patterns)):
        for j in range(0, 5):
            ftm_out.write(( i ).to_bytes(1, byteorder='little', signed=False)) # pattern

def writePatterns():
    ftm_out.write("PATTERNS".encode("ascii")) # Pattern block title
    ftm_out.write(b"\x00" * 8)
    ftm_out.write(b"\x05\x00\x00\x00") # Pattern block version (5)
    ftm_out.write( (patternsLength()).to_bytes(4, byteorder="little", signed=False) ) # Pattern block size

    for pattern in patterns:
        for bytelist in pattern:
            print(bytelist)
            ftm_out.write(bytelist)
    

def addToBytes(byteArray, size, amt):
    temp = int.from_bytes(byteArray, byteorder="little", signed=False) + amt
    return temp.to_bytes(size, byteorder="little", signed=False)

def patternsLength():
    totalLength = 0;
    for pattern in patterns:
        for byteArray in pattern:
            totalLength += len(byteArray)
    return totalLength

def newPattern(songIndex, channel, index):
    return [ songIndex.to_bytes(4, byteorder='little', signed=False),
             channel.to_bytes(4, byteorder='little', signed=False),
             index.to_bytes(4, byteorder='little', signed=False),
             (0).to_bytes(4, byteorder='little', signed=False) # defined rows amount (0 at the start)
            ]

def midiNoteToRow(note, velocity, rowIndex):
    notename = (note % 12) + 1
    octave = math.floor(note / 12) - 2

    return [ rowIndex.to_bytes(4, byteorder='little', signed=False),
             notename.to_bytes(1, byteorder='little', signed=False),
             octave.to_bytes(1, byteorder='little', signed=False),
             b"\x00\x10\x00\x00" ] # 0th instrument, no volume, no effects

def writeHdrAndParams(f):
    f.write("FamiTracker Module".encode("ascii"))
    f.write(b"\x40\x04\x00\x00") # Version number (0.4.3+)

    f.write("PARAMS".encode("ascii")) # Param block title
    f.write(b"\x00" * 10)
    f.write(b"\x06\x00\x00\x00") # Param block version (6)
    f.write(b"\x1d\x00\x00\x00") # Param block size
    f.write(b"\x00")             # Expansion chips disabled
    f.write(b"\x05\x00\x00\x00") # Number of channels (2a03 = 5ch)
    f.write(b"\x00\x00\x00\x00") # PAL mode disabled
    f.write(b"\x00\x00\x00\x00") # Default engine speed
    f.write(b"\x01\x00\x00\x00") # New vibrato mode enabled
    f.write((ROW_HIGHLIGHT_1).to_bytes(4, byteorder='little', signed=False))
    f.write((ROW_HIGHLIGHT_2).to_bytes(4, byteorder='little', signed=False))
    f.write(b"\x20\x00\x00\x00") # Speed/tempo split

main()
