from mido import *
from mido import MidiFile
from mido import tick2second, second2tick, tempo2bpm
import sys
import math

path_in = sys.argv[1]
path_out = sys.argv[2]

midi_in = MidiFile(path_in)
ftm_out = open(path_out, "wb")

patterns = [] # stores all pattern data

notes = [];

currentSq1Note = -1;

ROW_HIGHLIGHT_1 = 4
ROW_HIGHLIGHT_2 = 20

class Note:
    def __init__(self, p=72, t=0, ch=-1):
        self.pitch = p;
        self.time = t;
        self.channel = ch;

def main():
   
    writeHdrAndParams(ftm_out)

    currentPattern = 0
    patterns.append( newPattern(0,0,currentPattern) )

    global bpm, tpqn;

    ticksPerBeat = midi_in.ticks_per_beat
    print("Ticks per beat: " + str(ticksPerBeat))

    track = midi_in.tracks[0]
    for msg in track:
        if (msg.type == "set_tempo"):
            bpm = round(tempo2bpm(msg.tempo))
            print("Beats per minute: " + str(bpm))

    tpqn = int(60 / ( bpm / 60 ));

    trackTime = 0
    track = midi_in.tracks[1]
    for msg in track:
        trackTime += msg.time

        if (msg.type == "note_on" or msg.type == "note_off"):
            
            if (msg.velocity == 0 or msg.type == "note_off"):
                notes.append( Note(-msg.note, trackTime) );
            else:
                notes.append( Note(msg.note, trackTime) );

    currentPattern = 0;
    patternTime = 0;
    lastnotetime = 0;
    
    for note in notes:
        note.channel = 0; # 0 is pulse 1 for now

        moddur = note.time - lastnotetime
        moddur /= ticksPerBeat
        moddur /= bpm
        moddur *= 60 * 60
        print(str(moddur))
        
        patternTime += moddur

        patterns[currentPattern][3] = addToBytes( patterns[currentPattern][3], 4, 1)
        patterns[currentPattern].extend( midiNoteToRow(note.pitch, 15, round(patternTime) ) )

        if patternTime >= (tpqn * 4):
            currentPattern += 1
            patterns.append( newPattern(0,0,currentPattern) )
            patternTime %= (tpqn * 4);
        
        #print( "pitch: " + str( note.pitch) + " time: " + str( note.time)  + " channel: " + str( note.channel ) )
        lastnotetime = note.time

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
    ftm_out.write((1).to_bytes(4, byteorder='little', signed=False)) # speed
    ftm_out.write((150).to_bytes(4, byteorder='little', signed=False)) # tempo
    ftm_out.write(( tpqn * 4 ).to_bytes(4, byteorder='little', signed=False)) # rows per frame

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
            #print(bytelist)
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
    if (note < 0):
        notename = 0x0e
        octave = 4
    else:        
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
