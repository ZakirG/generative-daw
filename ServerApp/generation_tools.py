import random
from music21 import chord as music21_chords
import re
from constants import constants

ALLOWED_CHORD_SIZES_UPPER_BD = 6
ALLOWED_CHORD_SIZES_LOWER_BD = 3

def get_allowed_notes(key, scale, octave):
    possible_octaves = []
    if octave == 'any':
        possible_octaves = range(1,3)
        octave = 1
    else:
        possible_octaves = [octave]
        
    allowed_chromatic_notes = []
    for octave in possible_octaves:
        for note in constants['chromatic_scale']:
            allowed_chromatic_notes.append({'note' : note['note'], 'octave' : octave})
    
    return get_key_scale_notes(key, scale, octave, allowed_chromatic_notes)
    
def get_key_scale_notes(key, scale_code, octave, allowed_chromatic_notes):
    index_of_key = allowed_chromatic_notes.index({'note' : key.lower(), 'octave' : octave})
    notes_sorted_starting_at_root = allowed_chromatic_notes[index_of_key:] + allowed_chromatic_notes[:index_of_key]
    notes_sorted_starting_at_root = notes_sorted_starting_at_root * 2 # double list to make note selection circular
    print(notes_sorted_starting_at_root)
    intervals = constants['scales'][scale_code]['intervals']
    print(intervals)
    key_scale_notes = []
    i = 0
    for interval in intervals:
        print(notes_sorted_starting_at_root[i + interval])
        key_scale_notes.append( notes_sorted_starting_at_root[i + interval] )
        i = i + interval
    return key_scale_notes

def generate_random_melody(length, key, scale, octave):
    allowed_notes = get_allowed_notes(key, scale, octave)
    
    result = []
    for i in range(length):
        result.append([random.choice(allowed_notes)])
    
    print('melody:' + str(result))
    return result
    
def generate_random_chords(length, key, scale, octave):
    allowed_notes = get_allowed_notes(key, scale, octave)

    # Account for cases where there are very few allowed notes in the scale (like a pentatonic scale)
    upper_bd = min(ALLOWED_CHORD_SIZES_UPPER_BD, len(allowed_notes))
        
    allowed_chord_sizes = range(ALLOWED_CHORD_SIZES_LOWER_BD, upper_bd)
    
    result = []
    for i in range(length):
        num_notes_in_chord = random.choice(allowed_chord_sizes)
        chord = []
        unused_chord_tones = allowed_notes.copy()
        for j in range(num_notes_in_chord):
            generated_note_index = random.choice(range(len(unused_chord_tones)))
            chord.append(unused_chord_tones[generated_note_index])
            unused_chord_tones.pop(generated_note_index)
        result.append(chord)
            
    print('chords:' + str(result))
    return result
    
def determine_chord_name(chord):
    if len(chord) <= 2:
        return ''
    print('chord:', chord)
    notes = map(lambda x: x.upper(), chord)
    notes = list(map(lambda x: x.replace('S', '#'), notes))
    notes.reverse()
    print(notes)
    c = music21_chords.Chord(list(notes))
    full_name = c.pitchedCommonName
    print(c)
    print(full_name)
    abbreviation = full_name.replace('minor', 'min'
        ).replace('major', 'maj').replace('seventh', '7'
        ).replace('augmented', 'aug').replace('diminished', 'dim'
        ).replace('incomplete', '').replace('dominant', '').replace('-', ' ')

    if abbreviation.startswith('enharmonic equivalent'):
        try:
            enharmonicRegex = re.compile(r"enharmonic equivalent to (.*) above (.*)")
            matches = re.search(enharmonicRegex, abbreviation)
            abbreviation = matches.group(2) + ' ' + matches.group(1)
        except Exception as e:
            print(e)

    return abbreviation
    
def transpose_notes_to_grid(notes):
    grid = []
    timeStateLength = 8
    for step in range(timeStateLength):
        notes_at_this_step = []
        for note in notes:
            if note['timeStates'][step] == True:
                notes_at_this_step.append(note['note'])
        grid.append(notes_at_this_step)
    return grid
        
def name_chords_in_tracks(tracks):
    grid_by_tracks = list(map(transpose_notes_to_grid, tracks))
    chord_names_by_tracks = []
    for grid in grid_by_tracks:
        chord_names_by_tracks.append(list(map(lambda x: determine_chord_name(x), grid)))
    return chord_names_by_tracks
