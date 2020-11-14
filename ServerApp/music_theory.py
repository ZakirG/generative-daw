from constants import constants
import chord_knowledge
from chord_knowledge import chord_charts, good_voicings, chord_name_caches
from utils import roman_to_int, decide_will_event_occur, flatten_note_set
import music21
import midi_tools
from music21 import key as music21_key
from music21 import chord as music21_chords
import sys, traceback
import re
import random

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

def get_key_scale_letters(key_letter, scale_code):
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

def chords_are_equal(chord_a, chord_b):
    return set(flatten_note_set(chord_a)) == set(flatten_note_set(chord_b))

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


def convert_chord_to_cache_key(note_list):
    sequence = []
    time_state_index = 0
    for i in range(len(note_list)):
        sequence.append(note_list[i]['numeral'])
    return str(sequence)

def convert_sequence_to_cache_key(sequence):
    result = []
    time_state_index = 0
    for i in range(len(sequence)):
        result.append(sequence[i]['n'])
    return str(result)
  

def determine_chord_name_from_sequence(sequence, key, scale, track_number):
    if len(sequence) == 0:
        return '?', '?'
    
    # First check cache
    for octave in list(range(-3, 3, 1)):
        transposed_sequence = []
        for i in range(len(sequence)):
            transposed_sequence.append(sequence[i].copy())
            transposed_sequence[i]['n'] += octave * 12
        as_cache_key = convert_sequence_to_cache_key(transposed_sequence)
        if as_cache_key in chord_name_caches:
            return chord_name_caches[as_cache_key]
    
    # Now use music21

    notes = [x['n'] for x in sequence]
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

def note_to_roman_numeral(note, sorted_allowed_notes):
    """
    Translate a note choice in a scale to a roman numeral.
    Supports accidentals.
    Note: this function disrespects key signatures. It just biases sharps over flats.
    """
    degree = 1
    for note in sorted_allowed_notes:
        if are_notes_enharmonically_equivalent(note['note'], note['note']):
            break
        degree += 1
    
    modifier = '' # sharp or flat

    if degree == 8:
        # Case where we couldn't find the note in the scale.
        # We'll mark it as a sharpened or flattened scale degree.
        upper_neighbor = transpose_note_n_semitones(note, 1)
        lower_neighbor = transpose_note_n_semitones(note, -1)
        
        degree_upper = get_degree_for_root(upper_neighbor, sorted_allowed_notes)
        degree_lower = get_degree_for_root(lower_neighbor, sorted_allowed_notes)
        
        if degree_lower < 8:
            degree = degree_lower
            modifier = '#'
        else:
            degree = degree_upper
            modifier = 'b'
    
    roman_numeral = constants['roman_numerals_upper'][degree - 1] + modifier
    
    return roman_numeral

def roman_numeral_to_note(roman_numeral_in, allowed_notes):
    # Translate the roman numeral to a note in the context of a key.
    # Remove diminished marks, seventh chord notation, augmented notation, sharps, flats
    roman_numeral_upper = roman_numeral_in.replace('b',''
        ).replace('#','').replace('+','').replace('\xB0', ''
        ).replace('7', '').replace('6', '').upper()
    target_digit = roman_to_int(roman_numeral_upper)

    # Lists are zero-indexed while roman numerals are 1-indexed, so subtract 1 from the target_digit
    try:
        chord_root_note = allowed_notes[target_digit - 1]
    except Exception as e:
        # The chord root in question is not in the allowed scale. 
        exc_info = sys.exc_info()
        traceback.print_exception(*exc_info)
        print(e)
        return -1
    
    return chord_root_note

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
            full_allowed_notes = get_allowed_notes(key, parent_scale_code, [3])

        roman_numeral = note_to_roman_numeral(chord_root, full_allowed_notes)
        
        quality = chord_object.quality
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

def build_chord_from_voicing(voicing, chord_root, roman_numeral, octave_range):
    # Get the mode of the chord root so we know what the starting scale degree refers to
    if roman_numeral.isupper():
        scale_code = 'maj'
    else:
        scale_code = 'min'

    key_scale_notes = get_allowed_notes(chord_root['note'], scale_code, octave_range)

    start_degree_as_str = str(voicing['starting_scale_degree'])
    start_degree = 0
    if len(start_degree_as_str) > 1:
        modifier = 0
        if start_degree_as_str[1] == 'b':
            modifier = -1
        else:
            modifier = 1
        start_degree = (int(start_degree_as_str[0]) + modifier) 
    else:
        start_degree = int(start_degree_as_str)
 
    # TODO: this line has bias towards lower octaves. consider fixing that to better support large octave ranges.
    start_note = key_scale_notes[start_degree - 1] # Scale degrees are 1-indexed, while lists are zero-indexed
    chord = [start_note]
    prev_note = start_note
    for interval in voicing['intervals']:
        prev_note = transpose_note_n_semitones_with_octaves(prev_note, interval)
        chord.append(prev_note)

    # chord_with_octave_markers = [{ 'note': x, 'octave': random.choice(octaveRange) } for x in chord]
    return chord #_with_octave_markers

def transpose_notes_to_grid(notes):
        grid = []
        numBeats = len(notes[0]['timeStates'])
        for step in range(numBeats):
            notes_at_this_step = []
            for note in notes:
                if note['timeStates'][step] == True:
                    notes_at_this_step.append(note['note'])
            grid.append(notes_at_this_step)
        return grid

def name_chords_in_tracks(sequences, key, scale):
    last_time_step = 0
    all_chord_names = []
    for s in range(len(sequences)):
        chord_names = []
        current_chord_group = []
        for i in range(len(sequences[s])):
            note = sequences[s][i]
            if last_time_step != sequences[s][i]['t']:
                if len(current_chord_group) > 1:
                    name = determine_chord_name_from_sequence(current_chord_group, key, scale, s)
                    chord_names.append(name)
                current_chord_group = []
                last_time_step = sequences[s][i]['t']
            current_chord_group.append(note)
        # Final time step
        name = determine_chord_name_from_sequence(current_chord_group, key, scale, s)
        chord_names.append(name)
        current_chord_group = []
        all_chord_names.append(chord_names)
    
    chord_names = [ [ x[0] for x in track] for track in all_chord_names ]
    chord_degrees = [ [ x[1] for x in track] for track in all_chord_names ]
    

    return chord_names, chord_degrees

def chord_to_topline_int(chord):
    """
    Covert chord topline to an integer for the purpose of comparing
    topline height of adjacent chords.
    We just convert MIDI numeral here, as it has comparison built-in, assigning
    higher numerals to higher notes.
    """
    as_numerals = []
    for note in chord:
        numeral = midi_tools.note_to_numeral(note)
        as_numerals.append(numeral)
    
    return max(as_numerals)

def calculate_topline_distance(chord_a, chord_b):
    height_a = chord_to_topline_int(chord_a)
    height_b = chord_to_topline_int(chord_b)
    return abs(height_a - height_b)

def calculate_number_of_note_changes(chord_a, chord_b):
    to_int = lambda x: midi_tools.note_to_numeral(x)
    midi_int_a = map(to_int, chord_a)
    midi_int_b = map(to_int, chord_b)

    deletions = 0
    for numeral_a in midi_int_a:
        if numeral_a not in midi_int_b:
            deletions += 1
    
    additions = 0
    for numeral_b in midi_int_b:
        if numeral_b not in midi_int_a:
            additions += 1
        
    return max(additions, deletions)

def get_contour_directions_per_beat(topline_contour, number_of_chords_in_progression):
    """
    On each beat, the chord topline will need to respect a height constraint relative to the
    previous chord.
    
    We return an array of length "number_of_chords_in_progression" that contains
    directions for the next topline note to go in.

    # TODO: add support for "ramp" forms.
    """
    contour_code = topline_contour["code"]

    if contour_code == 'any':
        return ["any" for x in range(number_of_chords_in_progression) ]

    if contour_code == 'static':
        return ["any"] + ["equal" for x in range(number_of_chords_in_progression - 1) ]
    
    if contour_code == 'nonstatic':
        return ["any"] + ["unequal" for x in range(number_of_chords_in_progression - 1) ]
    
    if contour_code == 'up':
        return ["any"] + ["up" for x in range(number_of_chords_in_progression - 1) ]
    
    if contour_code == 'strictup':
        return ["any"] + ["strictup" for x in range(number_of_chords_in_progression - 1) ]
    
    if contour_code == 'down':
        return ["any"] + ["down" for x in range(number_of_chords_in_progression - 1) ]
    
    if contour_code == 'strictdown':
        return ["any"] + ["strictdown" for x in range(number_of_chords_in_progression - 1) ]
    
    midpoint = number_of_chords_in_progression // 2
    
    if contour_code == 'updown':
        relative_chord_heights = ["any"]
        relative_chord_heights += ["up" for x in range(0, midpoint - 1)  ]
        relative_chord_heights += ["down" for x in range(midpoint, number_of_chords_in_progression)  ]
        return relative_chord_heights
    
    if contour_code == 'downup':
        relative_chord_heights = ["any"]
        relative_chord_heights += ["down" for x in range(0, midpoint - 1)  ]
        relative_chord_heights += ["up" for x in range(midpoint, number_of_chords_in_progression)  ]
        return relative_chord_heights

    raise ValueError('Unknown contour code: ', contour_code)
    return []

def chord_passes_topline_contour_constraint(current_topline_direction, candidate_topline_position, previous_chord_topline_position):
    if current_topline_direction == "any" or previous_chord_topline_position is None:
        return True
    if current_topline_direction == "equal" and candidate_topline_position != previous_chord_topline_position:
        return False
    if current_topline_direction == "unequal" and candidate_topline_position == previous_chord_topline_position:
        return False
    if current_topline_direction == "strictup" and candidate_topline_position <= previous_chord_topline_position:
        return False
    if current_topline_direction == "strictdown" and candidate_topline_position >= previous_chord_topline_position:
        return False
    if current_topline_direction == "up" and candidate_topline_position < previous_chord_topline_position:
        return False
    if current_topline_direction == "down" and candidate_topline_position > previous_chord_topline_position:
        return False
    return True

def non_topline_note_passes_topline_distance_constraint(note, previous_chord_topline_position, max_topline_distance):
    note_position = note
    if not isinstance(note, int):
        note_position = midi_tools.note_to_numeral(note)
    return note_position - previous_chord_topline_position <= max_topline_distance

def topline_note_passes_topline_distance_constraint(note, previous_chord_topline_position, max_topline_distance):
    note_position = note
    if not isinstance(note, int):
        note_position = midi_tools.note_to_numeral(note)
    return abs(note_position - previous_chord_topline_position) <= max_topline_distance

def topline_note_passes_topline_constraints(current_topline_direction, candidate_note, previous_chord_topline_position, max_topline_distance):
    if previous_chord_topline_position is None:
        return True
    
    candidate_topline_note_position = candidate_note
    if not isinstance(candidate_topline_note_position, int):
        candidate_topline_note_position = midi_tools.note_to_numeral(candidate_topline_note_position)
    passes_topline_distance_constraint = topline_note_passes_topline_distance_constraint(candidate_topline_note_position, previous_chord_topline_position, max_topline_distance)
    
    if current_topline_direction == "any":
        passes_contour_constraint = True
    else:
        passes_contour_constraint = chord_passes_topline_contour_constraint(current_topline_direction, candidate_topline_note_position, previous_chord_topline_position)
    return passes_topline_distance_constraint and passes_contour_constraint

def non_topline_note_meets_topline_constraints(current_topline_direction, non_topline_note, previous_chord_topline_position, max_topline_distance):
    """
    If the contour is "down" and the topline distance is 3 semitones, any non-topline note above the
    previous chord's topline will be rejected.
    If the contour is "strictdown" and the topline distance is 3 semitones, any non-topline note above the
    previous chord's topline will be rejected.
    """
    if previous_chord_topline_position is None:
        return True
    note_position = non_topline_note
    if not isinstance(non_topline_note, int):
        note_position = midi_tools.note_to_numeral(non_topline_note)
    passes_topline_distance_constraint = non_topline_note_passes_topline_distance_constraint(note_position, previous_chord_topline_position, max_topline_distance)
    if current_topline_direction == "strictdown" and note_position >= previous_chord_topline_position:
        return False
    if current_topline_direction == "down" and note_position > previous_chord_topline_position:
        return False
    if current_topline_direction == "equal" and note_position > previous_chord_topline_position:
        return False
    return passes_topline_distance_constraint

def label_voicings_with_metadata(key, scale, octave_range):
    """
    The return value has the same structure as good_voicings, but with 
    added metadata on each voicing.

    A lovely function. As a musician, this is so useful to me. We perform metadata calculations
    on each chord voicing to better know whether to use it in a musical context, thereby constraining
    the solution space of randomized compositions. Having this data alone is useful in itself, and 
    the subject of many guitar tab encyclopedias. But being able to access it automatically in the
    process of filtering voicings that match a musical context goes beyond any encyclopedia.

    The result of this function is used by Generator.voicing_on_numeral_passes_constraints()
    """
    
    labeled_result = {}

    voicings_list = good_voicings.values()
    
    # Flatten list with list comprehension. The scale breakdowns are irrelevant since we're 
    # gonna filter out accidentals anyway
    voicings_list = [ voicing for voicing_group in voicings_list for voicing in voicing_group ]

    print('The voicings library has {} entries.'.format(len(voicings_list)))

    allowed_notes = get_key_scale_letters(key, scale)
    full_allowed_notes = allowed_notes
    
    if len(constants['scales'][scale]['intervals']) < 7:
        parent_scale_code = constants['scales'][scale]['parent_scale']
        full_allowed_notes = get_allowed_notes(key, parent_scale_code, [3])
        full_allowed_notes = [ note['note'] for note in full_allowed_notes]

    for voicing_group_key in good_voicings.keys():
        voicing_group = good_voicings[voicing_group_key]
        voicing_group_copy = []
        for voicing in voicing_group:
            roman_numerals_to_metadata = {}
            # Here we iterate over a full list of possible chord roman numerals, including non-diatonic ones
            # so as to calculate metadata
            for roman_numeral in chord_knowledge.all_roman:
                chord_root = roman_numeral_to_note(roman_numeral, full_allowed_notes)
                if chord_root == -1:
                    continue
                chord = build_chord_from_voicing(voicing, { 'note': chord_root, 'octave': octave_range[0] }, roman_numeral, octave_range)
                it_contains_accidentals = False
                it_fits_in_the_octave_range = True
                for chord_note in chord:
                    if chord_note['octave'] not in octave_range:
                        it_fits_in_the_octave_range = False
                    found_equivalent = False
                    for scale_note in allowed_notes:
                        are_equivalent = are_notes_enharmonically_equivalent(scale_note, chord_note['note'])
                        if are_equivalent:
                            found_equivalent = True
                    if not found_equivalent:
                        it_contains_accidentals = True
                
                roman_numerals_to_metadata[roman_numeral] = { 
                    'topline_position': chord_to_topline_int(chord),
                    'it_fits_in_the_octave_range': it_fits_in_the_octave_range,
                    'it_contains_accidentals': it_contains_accidentals
                }
            
            voicing_copy = voicing.copy()
            voicing_copy['roman_numerals_to_metadata'] = roman_numerals_to_metadata

            voicing_group_copy.append(voicing_copy)
        
        labeled_result[voicing_group_key] = voicing_group_copy
    return labeled_result

