from constants import constants
import music21
from music21 import key as music21_key
from music21 import chord as music21_chords
import sys, traceback
import re

def build_big_chromatic_scale_with_octaves(start_octave, num_octaves):
    chromatic_scale = [ { 'note': x['note'], 'octave': start_octave } for x in constants['chromatic_scale'] ]
    chromatic_scale_big = []
    for i in range(num_octaves):
        clone = [x.copy() for x in chromatic_scale]
        chromatic_scale_big += clone
    octaveAdder = 0
    for i in range(len(chromatic_scale_big)):
        octaveAdder =  i // 12
        chromatic_scale_big[i]['octave'] = int(chromatic_scale_big[i]['octave']) + octaveAdder
    return chromatic_scale_big

chromatic_scale_spanning_7_octaves = build_big_chromatic_scale_with_octaves(1, 7)

def transpose_note_n_semitones(note, n):
    chromatic_scale = [x['note'] for x in constants['chromatic_scale']]
    index_of_input = 0
    for i in range(len(chromatic_scale)):
        note_candidate = chromatic_scale[i]
        if are_notes_enharmonically_equivalent(note.lower(), note_candidate):
            index_of_input = i
            break

    index_of_transpose = (index_of_input + n) % 12
    return chromatic_scale[index_of_transpose]

def transpose_note_n_semitones_with_octaves(note, n):
    index = 0
    note_position_in_chromatic_scale = 0
    for note_candidate in chromatic_scale_spanning_7_octaves:
        if note_candidate['note'] == note['note'] and note_candidate['octave'] == note['octave']:
            note_position_in_chromatic_scale = index
            break
        index += 1
    
    return chromatic_scale_spanning_7_octaves[note_position_in_chromatic_scale + n]

def get_allowed_notes(key, scale_code, octaveRange):
    result = []
    for octave in octaveRange:
        allowed_chromatic_notes_in_octave = []
        for note in constants['chromatic_scale']:
            allowed_chromatic_notes_in_octave.append({'note' : note['note'], 'octave' : octave})
        result.extend(get_key_scale_notes(key, scale_code, octave, allowed_chromatic_notes_in_octave))
        
    return result
    
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

def get_key_scale_letters(key_letter, scale_code, octave):
    index_of_key = constants['chromatic_scale_letters'].index( key_letter.lower() )
    notes_sorted_starting_at_root = constants['chromatic_scale_letters'][index_of_key:] + constants['chromatic_scale_letters'][:index_of_key]
    notes_sorted_starting_at_root = notes_sorted_starting_at_root * 2 # big list to keep note selection circular
    intervals = constants['scales'][scale_code]['intervals']
    key_scale_letters = []
    i = 0
    for interval in intervals:
        key_scale_letters.append( notes_sorted_starting_at_root[i + interval] )
        i = i + interval
    # Rotate the result so that the tonic is first in the list
    return key_scale_letters[-1:] + key_scale_letters[:-1]

def are_notes_enharmonically_equivalent(note_a, note_b):
    note_a_compare = note_a.lower().replace('#', 's')
    note_b_compare = note_b.lower().replace('#', 's')
    if note_a == note_b:
        return True
    
    if note_a in constants['enharmonic_equivalents'] and constants['enharmonic_equivalents'][note_a] == note_b:
        return True
    
    if note_b in constants['enharmonic_equivalents'] and constants['enharmonic_equivalents'][note_b] == note_a:
        return True
    
    return False

def correct_mispelled_enharmonic_notes_according_to_key_sig(key, scale_code, note_set):
    """
    This function is no longer useful. Turns out you can pass MIDI to music21.
    TODO: delete this function
    """
    tonic = key.upper().replace('S', '#')
    if tonic[-1].isnumeric():
        tonic = tonic[:-1]
    if len(tonic) > 1 and tonic[-1] == 'B':
        tonic[-1] = '-'
    key_of_tonic = music21_key.Key(tonic, constants['scales'][scale_code]['name'])
    notes_in_key = [key_of_tonic.pitchFromDegree(x).name for x in range(1,8)]
    notes_in_key = list(map(lambda x: x.replace('-', 'b').replace('#', 's').lower(), notes_in_key))
    correct_spelling_of_note_set = []
    for note in note_set:
        appended_already = False
        if note not in notes_in_key:
            for note_from_key in notes_in_key:
                if are_notes_enharmonically_equivalent(note_from_key, note):
                    correct_spelling_of_note_set.append(note_from_key)
                    appended_already = True
                    break
        if appended_already == False:
            correct_spelling_of_note_set.append(note)
    return correct_spelling_of_note_set

def determine_chord_name(chord, key, scale):
    """
    Returns a tuple (common_letter_name, roman_numeral_name)
    """
    if len(chord) <= 2:
        return ('', '')

    notes = map(lambda x: x.upper(), chord)
    notes = list(map(lambda x: x.replace('S', '#'), notes))
    notes.reverse()
    notes = list(map(lambda x: music21.pitch.Pitch(x).midi, notes))
    c = music21_chords.Chord(list(notes))
    full_name = c.pitchedCommonName
    abbreviation = full_name.replace('minor', 'min'
        ).replace('major', 'maj').replace('seventh', '7'
        ).replace('augmented', 'aug').replace('diminished', 'dim'
        ).replace('incomplete', '').replace('dominant', '').replace('-', ' '
        ).replace('E#', 'F')
    
    

    if abbreviation.startswith('enharmonic equivalent'):
        enharmonicRegex = re.compile(r"enharmonic equivalent to (.*) above (.*)")
        matches = re.search(enharmonicRegex, abbreviation)
        abbreviation = matches.group(2) + ' ' + matches.group(1)
        
    return (abbreviation, determine_chord_roman_name(abbreviation, key, scale, c))

def get_degree_for_root(chord_root, sorted_allowed_notes):
    degree = 1
    for note in sorted_allowed_notes:
        if are_notes_enharmonically_equivalent(note['note'], chord_root):
            break
        degree += 1
    return degree

def determine_chord_roman_name(chord_name, key, scale, chord_object):
    try:
        if len(chord_name.strip()) == 0 or chord_name.startswith('forte'):
            return ''
        
        pieces = chord_name.split()
        chord_root = pieces[0].lower().replace('#', 's')
        sorted_allowed_notes = get_allowed_notes(key, scale['code'], [0])
        
        full_allowed_notes = sorted_allowed_notes
        scale_code = scale['code']
        if len(constants['scales'][scale_code]['intervals']) < 7:
            # If we're working in a derived scale like a pentatonic, 
            # use the full parent scale to find the correct scale degree.
            parent_scale_code = constants['scales'][scale_code]['parent_scale']
            full_allowed_notes = get_allowed_notes(key, parent_scale_code, 3)

        degree = get_degree_for_root(chord_root, full_allowed_notes)
        modifier = '' # sharp or flat

        if degree == 8:
            # Case where we couldn't find the note in the scale.
            # We'll mark it as a sharpened or flattened scale degree.
            upper_neighbor = transpose_note_n_semitones(chord_root, 1)
            lower_neighbor = transpose_note_n_semitones(chord_root, -1)
            
            degree_upper = get_degree_for_root(upper_neighbor, sorted_allowed_notes)
            degree_lower = get_degree_for_root(lower_neighbor, sorted_allowed_notes)
            
            if degree_lower < 8:
                degree = degree_lower
                modifier = '#'
            else:
                degree = degree_upper
                modifier = 'b'
        
        quality = chord_object.quality
        roman_numeral = constants['roman_numerals_upper'][degree - 1] + modifier

        is_major = 'major' in pieces or 'maj' in pieces
        is_incomplete_dominant_in_major = 'maj' in scale_code and ('min' not in pieces and ('dominant-seventh' in pieces or '7' in pieces))
        
        if is_major or is_incomplete_dominant_in_major:
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
        print('Error: failed to find roman numeral for chord_name: ', chord_name)
        print('chord object: ',chord_object)
        print('scale: ', scale)
        print('key: ', key)

        return ''

def build_chord_from_voicing(voicing, chord_root, roman_numeral, octaveRange):
    # Get the mode of the chord root so we know what the starting scale degree refers to
    if roman_numeral.isupper():
        scale_code = 'maj'
    else:
        scale_code = 'min'

    # key_scale_notes = get_key_scale_letters(chord_root['note'], scale_code, 3)
    key_scale_notes = get_allowed_notes(chord_root['note'], scale_code, octaveRange)

    start_degree = voicing['starting_scale_degree']
    # Scale degrees are 1-indexed, while lists are zero-indexed
    start_note = key_scale_notes[start_degree - 1]
    chord = [start_note]
    prev_note = start_note
    for interval in voicing['intervals']:
        prev_note = transpose_note_n_semitones_with_octaves(prev_note, interval)
        chord.append(prev_note)

    # chord_with_octave_markers = [{ 'note': x, 'octave': random.choice(octaveRange) } for x in chord]
    return chord #_with_octave_markers