import random
from constants import constants, chord_leading_chart
from utils import roman_to_int
from client_logging import ClientLogger
from music_theory import determine_chord_name, get_allowed_notes, transpose_note_up_n_semitones
ClientLogger = ClientLogger()

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

def build_chord_with_root(chosen_target_degree, key, scale, 
    allowed_notes, chord_size_lower_bound, chord_size_upper_bound, octave):

    roman_numeral_upper = chosen_target_degree.replace('b',''
        ).replace('#','').replace('+','').replace('\xB0', ''
        ).upper()
    target_digit = roman_to_int(roman_numeral_upper)
    note_choices_for_result = []

    # Lists are zero-indexed while roman numerals are 1-indexed, so subtract 1 from the target_digit
    try:
        chord_root_note = allowed_notes[target_digit - 1]
    except Exception:
        # The chord root in question is not in the allowed scale. 
        # Therefore, we cannot proceed.
        return -1
    
    note_choices_for_result.append(chord_root_note['note'])

    quality = 'minor'
    if chosen_target_degree.isupper():
        quality = 'major'

    is_diminished =  '\xB0' in chosen_target_degree
    is_augmented = '+' in chosen_target_degree

    third_of_chord = None
    if quality == 'major':
        third_of_chord = transpose_note_up_n_semitones(chord_root_note['note'], 4)
    elif quality == 'minor':
        third_of_chord = transpose_note_up_n_semitones(chord_root_note['note'], 3)
    note_choices_for_result.append(third_of_chord)
    
    fifth_of_chord = transpose_note_up_n_semitones(chord_root_note['note'], 7)
    if is_diminished:
        # diminished chord
        fifth_of_chord = transpose_note_up_n_semitones(chord_root_note['note'], 6)
    elif is_augmented:
        # augmented chord
        fifth_of_chord = transpose_note_up_n_semitones(chord_root_note['note'], 8)
    note_choices_for_result.append(fifth_of_chord)
    
    semitones_up_to_seventh = 11 # major seventh
    if is_diminished:
        semitones_up_to_seventh = 9
    elif is_augmented or quality == 'minor':
        semitones_up_to_seventh = 10
    seventh_of_chord = transpose_note_up_n_semitones(chord_root_note['note'], semitones_up_to_seventh)
    note_choices_for_result.append(seventh_of_chord)
    
    # Diminished chords sound good with major ninths too
    semitones_up_to_ninth = 14
    if is_augmented:
        # Augmented sharp-nine chords sound cool
        semitones_up_to_ninth = 15
    ninth_of_chord = transpose_note_up_n_semitones(chord_root_note['note'], semitones_up_to_ninth)
    note_choices_for_result.append(ninth_of_chord)

    # Avoiding major sharp 11ths for now. Sharp 11ths on a major chord are done in jazz, but my code doesn't yet support accidentals.
    # if quality == 'major':
    #   # Sharpened 11th for major chord
    #    eleventh_of_chord = transpose_note_up_n_semitones(chord_root_note['note'], 18)
    if quality == 'minor':
        eleventh_of_chord = transpose_note_up_n_semitones(chord_root_note['note'], 17)
        note_choices_for_result.append(eleventh_of_chord)
    
    if quality == 'major':
        # 13th is the 6th
        sixth_of_chord = transpose_note_up_n_semitones(chord_root_note['note'], 9)
        note_choices_for_result.append(sixth_of_chord)
    
    # Avoiding minor 13ths for now, because minor sixths chords usually sharpen to get a major sixth, 
    # and my code doesn't support accidentals yet.
    # if quality == 'minor':
    #     sixth_of_chord = transpose_note_up_n_semitones(chord_root_note['note'], 9)
    #     note_choices_for_result.append(sixth_of_chord)

    # print('possible notes: ', note_choices_for_result)
    
    
    # As a rule, let's require the chord root in the chord.
    result_chord = [note_choices_for_result[0]]

    # Eliminate note choices outside of the key.
    allowed_letters = [x['note'] for x in allowed_notes]
    chord_size = min(random.choice(range(chord_size_lower_bound, chord_size_upper_bound + 1)), len(allowed_letters))
    note_choices_for_result = [x for x in note_choices_for_result if x in allowed_letters]

    if len(note_choices_for_result) < chord_size:
        # Note enough notes in the scale to build a decent chord on this root.
        return -1
    result_chord.extend(pick_n_random_notes(note_choices_for_result[1:], chord_size - 1))
    
    # For now, let's naively place these notes in the same octave. This will limit the voicings
    # we can create. TODO: Handle this better to produce more interesting voicings.
    result_chord_notes = [ {'note': x, 'octave': octave} for x in result_chord ]
    return result_chord_notes

def generate_chords(length, key, scale, octave, chord_size_lower_bound, chord_size_upper_bound, disallow_repeats, use_chord_leading):
    allowed_notes = get_allowed_notes(key, scale, octave)

    # Account for cases where there are very few allowed notes in the scale (like a pentatonic scale)
    upper_bd = min(chord_size_upper_bound, len(allowed_notes))
    allowed_chord_sizes = range(chord_size_lower_bound, upper_bd + 1)
    if upper_bd == chord_size_lower_bound:
        allowed_chord_sizes = [upper_bd]
    
    result = []
    previous_chord = []
    previous_chord_name = ''
    for i in range(length):
        num_notes_in_chord = random.choice(allowed_chord_sizes)

        candidate_chord = None
        generation_method = '?'
        if use_chord_leading and len(previous_chord) > 0 and previous_chord_name[1] != '':
            previous_chord_degree = previous_chord_name[1].split()[0]

            # The chosen scale tells us which chord leading chart to use
            quality = 'minor'
            if 'maj' in scale:
                quality = 'major'

            if previous_chord_degree in chord_leading_chart[quality]:
                leading_targets = chord_leading_chart[quality][previous_chord_degree].copy()
                # ClientLogger.log('Allowed leading targets for {} are {}'.format(previous_chord_degree, leading_targets))
                
                # Now we attempt to build a chord with one of the leading targets.
                # This may take multiple tries, as certain scales lack certain leading targets.
                # If all leading targets fail to produce a chord, we abort and stick with the previous randomly chosen chord.
                leading_chord = -1
                while leading_chord == -1 and len(leading_targets) > 0:
                    chosen_target_degree = random.choice(leading_targets)
                    # TODO: use global_key here instead of key
                    leading_chord = build_chord_with_root(chosen_target_degree, key, scale, allowed_notes, \
                        chord_size_lower_bound, chord_size_upper_bound, octave)
                
                    if leading_chord != -1:
                        candidate_chord = leading_chord
                        # ClientLogger.log('Applying chord leading rules to lead ({}) -> ({})'.format(previous_chord_name[1], chosen_target_degree))
                        # ClientLogger.log('Built chord {} on {}.'.format(determine_chord_name(flatten_note_set(leading_chord), key, constants['scales'][scale])[0], chosen_target_degree))
                        generation_method = 'applied chord leading to lead {} -> {}'.format(previous_chord_name[1].split()[0], chosen_target_degree)
                    
                    leading_targets.remove(chosen_target_degree)
                # if leading_chord == -1:
                #     ClientLogger.log('Failed to apply chord-leading chart to {} in {} {}.'.format(previous_chord_degree, key, scale))
           
        if candidate_chord is None:
            generation_method = 'picked {} scale notes at random'.format(num_notes_in_chord)
            candidate_chord = pick_n_random_notes(allowed_notes, num_notes_in_chord)
        
        # If repeats are disallowed, allow up to 6 retries to find a different noteset.
        if disallow_repeats:
            max_retries = 6
            retries = 0
            while set(flatten_note_set(previous_chord)) == set(flatten_note_set(candidate_chord)) and retries < max_retries:
                # ClientLogger.log('Accidentally repeated a chord twice in a row. Regenerating randomly...')
                retries += 1
                num_notes_in_chord = random.choice(allowed_chord_sizes)
                candidate_chord = pick_n_random_notes(allowed_notes, num_notes_in_chord)
                generation_method = 'picked {} scale notes at random'.format(num_notes_in_chord)

        result.append(candidate_chord)
        previous_chord = candidate_chord
        previous_chord_name = determine_chord_name(flatten_note_set(previous_chord), key, constants['scales'][scale])
        degree = None
        try:
            degree = previous_chord_name[1].split()[0]
        except Exception as e:
            pass
        ClientLogger.log('Added {} ({}). Generation method: {}'.format(previous_chord_name[0], degree, generation_method))
    
    return result

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