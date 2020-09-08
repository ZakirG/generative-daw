import random
from music21 import chord as music21_chords
import re
from constants import constants
import sys
import traceback

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
    intervals = constants['scales'][scale_code]['intervals']
    key_scale_notes = []
    i = 0
    for interval in intervals:
        key_scale_notes.append( notes_sorted_starting_at_root[i + interval] )
        i = i + interval
    # Rotate the result so that the tonic is first in the list
    return key_scale_notes[-1:] + key_scale_notes[:-1]

def generate_melody(length, key, scale, octave, disallow_repeats):
    allowed_notes = get_allowed_notes(key, scale, octave)
    
    result = []
    previous_note = None
    for i in range(length):
        candidate_note = random.choice(allowed_notes)
        # If repeats are disallowed, allow up to 6 retries to find a different noteset.
        if disallow_repeats and previous_note is not None:
            max_retries = 6
            retries = 0
            while set(flatten_note_set([previous_note])) == set(flatten_note_set([candidate_note])) and retries < max_retries:
                retries += 1
                candidate_note = random.choice(allowed_notes)

        result.append([candidate_note])
        previous_note = candidate_note
    
    return result

def pick_n_random_notes(allowed_notes_in, n):
    allowed_notes = allowed_notes_in.copy()
    note_set = []
    for j in range(n):
        random_index = random.choice(range(len(allowed_notes)))
        note_set.append(allowed_notes[random_index])
        allowed_notes.pop(random_index)
    return note_set

def flatten_note_set(note_set):
    # Transform from [{'note': 'b', 'octave': 3}, {'note': 'd', 'octave': 3}, {'note': 'e', 'octave': 3}]
    # to ['b3', 'd3', 'e3']
    return [x['note'] + str(x['octave']) for x in note_set]

def generate_chords(length, key, scale, octave, chord_size_lower_bound, chord_size_upper_bound, disallow_repeats):
    allowed_notes = get_allowed_notes(key, scale, octave)

    # Account for cases where there are very few allowed notes in the scale (like a pentatonic scale)
    upper_bd = min(chord_size_upper_bound, len(allowed_notes))
    allowed_chord_sizes = range(chord_size_lower_bound, upper_bd + 1)
    if upper_bd == chord_size_lower_bound:
        allowed_chord_sizes = [upper_bd]
    
    result = []
    previous_chord = []
    for i in range(length):
        num_notes_in_chord = random.choice(allowed_chord_sizes)
        candidate_chord = pick_n_random_notes(allowed_notes, num_notes_in_chord)
        # If repeats are disallowed, allow up to 6 retries to find a different noteset.
        if disallow_repeats:
            max_retries = 6
            retries = 0
            while set(flatten_note_set(previous_chord)) == set(flatten_note_set(candidate_chord)) and retries < max_retries:
                retries += 1
                num_notes_in_chord = random.choice(allowed_chord_sizes)
                candidate_chord = pick_n_random_notes(allowed_notes, num_notes_in_chord)

        result.append(candidate_chord)
        previous_chord = candidate_chord
            
    return result

def determine_chord_name(chord, key, scale):
    if len(chord) <= 2:
        return ('', '')
    notes = map(lambda x: x.upper(), chord)
    notes = list(map(lambda x: x.replace('S', '#'), notes))
    notes.reverse()
    c = music21_chords.Chord(list(notes))
    full_name = c.pitchedCommonName
    abbreviation = full_name.replace('minor', 'min'
        ).replace('major', 'maj').replace('seventh', '7'
        ).replace('augmented', 'aug').replace('diminished', 'dim'
        ).replace('incomplete', '').replace('dominant', '').replace('-', ' ')
        
    if abbreviation.startswith('enharmonic equivalent'):
        enharmonicRegex = re.compile(r"enharmonic equivalent to (.*) above (.*)")
        matches = re.search(enharmonicRegex, abbreviation)
        abbreviation = matches.group(2) + ' ' + matches.group(1)
        
    return (abbreviation, determine_chord_degree(abbreviation, key, scale, c))

def get_degree_for_root(chord_root, sorted_allowed_notes):
    degree = 1
    for note in sorted_allowed_notes:
        if note['note'] == chord_root:
            break
        degree += 1
    return degree


def determine_chord_degree(chord_name, key, scale, chord_object):
    try:
        if len(chord_name.strip()) == 0:
            return ''

        pieces = chord_name.split()
        chord_root = pieces[0].lower().replace('#', 's')
        sorted_allowed_notes = get_allowed_notes(key, scale['code'], 0)
        
        degree = get_degree_for_root(chord_root, sorted_allowed_notes)
        modifier = '' # sharp or flat

        if degree == 8:
            upper_neighbor = ''
            lower_neighbor = ''
            if len(chord_root) == 1:
                upper_neighbor = chord_root + 's'
            else:
                lower_neighbor = chord_root[0]
            if len(upper_neighbor) > 0:
                degree = get_degree_for_root(upper_neighbor, sorted_allowed_notes)
                modifier = 'b'
            if len(lower_neighbor) > 0:
                degree = get_degree_for_root(lower_neighbor, sorted_allowed_notes)
                modifier = '#'

        quality = chord_object.quality
        roman_numeral = constants['roman_numerals_upper'][degree - 1] + modifier

        if quality == 'major' or 'maj' in pieces:
            return roman_numeral + ' ' + ' '.join(pieces[1:])
        if quality == 'augmented':
            return roman_numeral + '+ ' +  ' '.join(pieces[1:])
        if quality == 'minor':
            return roman_numeral.lower() + ' ' + ' '.join(pieces[1:])
        if quality == 'diminished':
            return roman_numeral.lower() + '\xB0 ' +  ' '.join(pieces[1:])
        
        return roman_numeral.lower() + ' ' + ' '.join(pieces[1:])
    except Exception as e:
        exc_info = sys.exc_info()
        print('Exception: ', e)
        traceback.print_exception(*exc_info)
        return ''


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

def name_chords_in_tracks(tracks, key, scale):
    grid_by_tracks = list(map(transpose_notes_to_grid, tracks))
    coupled = []
    for grid in grid_by_tracks:
        coupled.append(list(map(lambda x: determine_chord_name(x, key, scale), grid)))
    
    chord_names_by_tracks = [ [x[0] for x in track] for track in coupled ]
    chord_degrees_by_tracks = [ [x[1] for x in track] for track in coupled ]
    
    return chord_names_by_tracks, chord_degrees_by_tracks