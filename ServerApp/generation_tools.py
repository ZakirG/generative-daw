import random
from constants import constants
from chord_knowledge import chord_leading_chart, good_voicings, chord_charts
from utils import roman_to_int, decide_will_event_occur, flatten_note_set, pick_n_random_notes
from client_logging import ClientLogger
from music_theory import determine_chord_name, get_allowed_notes, \
    transpose_note_n_semitones, build_chord_from_voicing, label_voicings_by_roman_numeral, \
    roman_numeral_to_note, chords_are_equal
import sys, traceback
ClientLogger = ClientLogger()

class Generator:
    def __init__(self, key, scale, length, chance_to_use_chord_leading, chance_to_use_voicing_from_library, disallow_repeats, chord_size_bounds, octave_range, v_must_be_dom_7, chance_to_use_non_diatonic_chord):
        self.key = key
        self.scale = scale
        self.length = length
        self.chance_to_use_chord_leading = chance_to_use_chord_leading
        self.chance_to_use_voicing_from_library = chance_to_use_voicing_from_library
        self.disallow_repeats = disallow_repeats
        self.chord_size_upper_bound = chord_size_bounds[1]
        self.chord_size_lower_bound = chord_size_bounds[0]
        self.octave_range = octave_range
        self.v_must_be_dom_7 = v_must_be_dom_7
        self.allow_neapolitan_chords = True
        self.chance_to_use_non_diatonic_chord = chance_to_use_non_diatonic_chord

        # Labeling chord voicings with acceptable roman numerals per scale to preserve diatonicity.
        # This result is specific to the scale of interest. But not its key.
        self.labeled_voicings = label_voicings_by_roman_numeral(key, scale)
            
    def generate_melody(self, length):
        allowed_notes = get_allowed_notes(self.key, self.scale, self.octave_range)
        
        result = []
        previous_note = None
        for i in range(self.length):
            candidate_note = random.choice(allowed_notes)
            # If repeats are disallowed, allow up to 6 retries to find a different noteset.
            if self.disallow_repeats and previous_note is not None:
                max_retries = 6
                retries = 0
                while set(flatten_note_set([previous_note])) == set(flatten_note_set([candidate_note])) and retries < max_retries:
                    retries += 1
                    candidate_note = random.choice(allowed_notes)

            result.append([candidate_note])
            previous_note = candidate_note
        
        return result

    def build_chord_with_root_randomly(self, chord_root_note, chosen_target_degree, allowed_notes):
        note_choices_for_result = []

        quality = 'minor'
        if chosen_target_degree.isupper():
            quality = 'major'

        is_diminished =  '\xB0' in chosen_target_degree
        is_augmented = '+' in chosen_target_degree

        third_of_chord = None
        if quality == 'major':
            third_of_chord = transpose_note_n_semitones(chord_root_note['note'], 4)
        elif quality == 'minor':
            third_of_chord = transpose_note_n_semitones(chord_root_note['note'], 3)

        # As a rule, let's require the chord root and the third are the chord.
        result_chord = [chord_root_note['note'], third_of_chord]
        
        fifth_of_chord = transpose_note_n_semitones(chord_root_note['note'], 7)
        if is_diminished:
            # diminished chord
            fifth_of_chord = transpose_note_n_semitones(chord_root_note['note'], 6)
        elif is_augmented:
            # augmented chord
            fifth_of_chord = transpose_note_n_semitones(chord_root_note['note'], 8)
        note_choices_for_result.append(fifth_of_chord)
        
        semitones_up_to_seventh = 11 # major seventh
        if is_diminished:
            semitones_up_to_seventh = 9
        elif is_augmented or quality == 'minor':
            semitones_up_to_seventh = 10
        seventh_of_chord = transpose_note_n_semitones(chord_root_note['note'], semitones_up_to_seventh)
        note_choices_for_result.append(seventh_of_chord)
        
        # Diminished chords sound good with major ninths too
        semitones_up_to_ninth = 14
        if is_augmented:
            # Augmented sharp-nine chords sound cool
            semitones_up_to_ninth = 15
        ninth_of_chord = transpose_note_n_semitones(chord_root_note['note'], semitones_up_to_ninth)
        note_choices_for_result.append(ninth_of_chord)

        # Avoiding major sharp 11ths for now. Sharp 11ths on a major chord are done in jazz, but my code doesn't yet support accidentals.
        # if quality == 'major':
        #   # Sharpened 11th for major chord
        #    eleventh_of_chord = transpose_note_n_semitones(chord_root_note['note'], 18)
        if quality == 'minor':
            eleventh_of_chord = transpose_note_n_semitones(chord_root_note['note'], 17)
            note_choices_for_result.append(eleventh_of_chord)
        
        if quality == 'major':
            # 13th is the 6th
            sixth_of_chord = transpose_note_n_semitones(chord_root_note['note'], 9)
            note_choices_for_result.append(sixth_of_chord)
        
        # Avoiding minor 13ths for now, because minor sixths chords usually sharpen to get a major sixth, 
        # and my code doesn't support accidentals yet.
        # if quality == 'minor':
        #     sixth_of_chord = transpose_note_n_semitones(chord_root_note['note'], 9)
        #     note_choices_for_result.append(sixth_of_chord)

        # print('possible notes: ', note_choices_for_result)
        

        # Eliminate note choices outside of the self.key.
        allowed_letters = [x['note'] for x in allowed_notes]
        chord_size = min(random.choice(range(self.chord_size_lower_bound, self.chord_size_upper_bound + 1)), len(allowed_letters))
        note_choices_for_result = [x for x in note_choices_for_result if x in allowed_letters]

        if len(note_choices_for_result) < chord_size:
            # Note enough notes in the scale to build a decent chord on this root.
            return -1
        result_chord.extend(pick_n_random_notes(note_choices_for_result[1:], chord_size - 1))
        
        result_chord_notes = [ {'note': x, 'octave': random.choice(self.octave_range)} for x in result_chord ]
        return result_chord_notes

    def build_chord_with_random_good_voicing(self, chosen_target_degree, chord_root_note):
        """
        Returns (built_chord, [chord_letter_name, chord_roman_name], chosen_voicing['name'])
        """
        # We can select a voicing by its quality instead of being constrained to the scale.
        # This allows for altered notes, non-diatonic chords, borrowed chords.
        # voicings_for_quality = []
        # if chosen_target_degree == 'V' and self.v_must_be_dom_7:
        #     voicings_for_quality = self.labeled_voicings['dominant-7']
        # elif chosen_target_degree == 'V' and not self.v_must_be_dom_7:
        #     voicings_for_quality = self.labeled_voicings['dominant-7'] + self.labeled_voicings['major']
        # elif '\xB0' in chosen_target_degree:
        #     voicings_for_quality = self.labeled_voicings['diminished']
        # elif '+' in chosen_target_degree and chosen_target_degree.isupper():
        #     voicings_for_quality = self.labeled_voicings['augmented']
        # elif chosen_target_degree == 'IV':
        #     voicings_for_quality = self.labeled_voicings['major'] # + labeled_voicings['lydian']
        # elif chosen_target_degree.isupper():
        #     voicings_for_quality = self.labeled_voicings['major']
        # elif chosen_target_degree == 'v' and self.chance_to_use_non_diatonic_chord > 0:
        #     # V Dominant 7 chords are sometimes borrowed for use in a minor context
        #     # Contains an accidental, from the harmonic minor
        #     voicings_for_quality = self.labeled_voicings['minor'] + self.labeled_voicings['dominant-7']
        # else:
        #     voicings_for_quality = self. labeled_voicings['minor']
        # elif chosen_target_degree == 'iv' and self.allow_accidentals:
            # The Neapolitan chord https://www.youtube.com/watch?v=K8Z6MTonoXE&ab_channel=MusicTheoryForGuitar
        
        applicable_voicings = []
        for voicing_group in self.labeled_voicings.values():
            for voicing in voicing_group:
                chord_size = len(voicing['intervals']) + 1
                matches_chord_size_constraint = (chord_size >= self.chord_size_lower_bound and chord_size <= self.chord_size_upper_bound)
                matches_octave_constraint = True # TODO
                matches_roman_numeral_constraint = True
                
                # Perform weighted coin-toss: will we allow a non-diatonic chord?
                # Technically, this configuration option is misleadingly named. It's not the
                # chance to allow a non-diatonic chord, it's the chance to not reject a chord
                # for being non-diatonic.
                reject_non_diatonic_chord =  decide_will_event_occur(1 - self.chance_to_use_non_diatonic_chord)

                # TODO: add exceptions here, if configured by the user, for specific borrowed chord techniques (like 
                # allowing altered notes in dominants)

                if chosen_target_degree not in voicing['allowed_roman_numerals'] and reject_non_diatonic_chord:
                    matches_roman_numeral_constraint = False
                
                if matches_chord_size_constraint and matches_octave_constraint and matches_roman_numeral_constraint:
                    applicable_voicings.append(voicing)
        
        if len(applicable_voicings) > 0:
            chosen_voicing = random.choice(applicable_voicings).copy()
            built_chord = build_chord_from_voicing(chosen_voicing, chord_root_note, chosen_target_degree, self.octave_range)
            chord_letter_name = chord_root_note['note'].upper().replace('S', '#') + ' ' + chosen_voicing['name']
            chord_roman_name = chosen_target_degree + ' ' + chosen_voicing['name']
            return built_chord, [chord_letter_name, chord_roman_name], chosen_voicing['name']
        return -1, -1, -1

    def build_chord_with_root(self, chosen_target_degree, allowed_notes):
        """
        Returns (built_chord, name_of_chord, generation_method)
        """
        chord_root_note = roman_numeral_to_note(chosen_target_degree, allowed_notes)

        # Perform weighted coin toss
        use_chord_voicing_from_library = decide_will_event_occur(self.chance_to_use_voicing_from_library)

        if use_chord_voicing_from_library:
            # First, lets filter the voicings library down to match the chord size and roman numeral constraints.
            built_chord, name_of_chord, name_of_voicing = self.build_chord_with_random_good_voicing(chosen_target_degree, chord_root_note)
            if built_chord != -1:
                # print('Choosing to voice {} with voicing {}'.format(chosen_target_degree, chosen_voicing))
                # print('chord root note: ', chord_root_note)
                generation_method = "- Decided to voice {} as a {}".format(chosen_target_degree, name_of_voicing)
                return (built_chord, name_of_chord, generation_method)

        # If all else fails, build it randomly.
        built_chord = self.build_chord_with_root_randomly(chord_root_note, chosen_target_degree, allowed_notes)
        generation_method = '- Built {} by picking scale notes at random.'.format(chosen_target_degree)
        return (built_chord, None, generation_method)

    def generate_chords(self):
        allowed_notes = get_allowed_notes(self.key, self.scale, self.octave_range)

        # Account for cases where there are very few allowed notes in the scale (like a pentatonic scale)
        upper_bd = min(self.chord_size_upper_bound, len(allowed_notes))
        allowed_chord_sizes = range(self.chord_size_lower_bound, upper_bd + 1)
        if upper_bd == self.chord_size_lower_bound:
            allowed_chord_sizes = [upper_bd]
        
        result_chord_progression = []
        result_chord_names = []
        previous_chord = []
        previous_chord_name = '', ''
        for i in range(self.length):
            num_notes_in_chord = random.choice(allowed_chord_sizes)

            candidate_chord = None
            name_of_candidate_chord = None
            generation_method = '?'

            # Perform weighted coin toss
            use_chord_leading = decide_will_event_occur(self.chance_to_use_chord_leading)

            if use_chord_leading and len(previous_chord) > 0 and previous_chord_name[1] != '':
                # The chosen scale tells us which chord leading chart to use
                quality = 'minor'
                if 'maj' in self.scale:
                    quality = 'major'

                if previous_chord_degree in chord_leading_chart[quality]:
                    leading_targets = chord_leading_chart[quality][previous_chord_degree].copy()
                    # Now we attempt to build a chord with one of the leading targets.
                    # This may take multiple tries, as certain scales lack certain leading targets.
                    # If all leading targets fail to produce a chord, we abort and use a different chord creation method.
                    leading_chord = -1
                    while leading_chord == -1 and len(leading_targets) > 0:
                        chosen_target_degree = random.choice(leading_targets)
                        # TODO: use global_key here instead of key
                        leading_chord, name_of_chord, __generation_method = self.build_chord_with_root(chosen_target_degree, allowed_notes)
                    
                        if leading_chord != -1:
                            candidate_chord = leading_chord
                            name_of_candidate_chord = name_of_chord
                            generation_method = '\t- Used {} chord leading chart suggestion {} -> {}. '.format(quality, previous_chord_name[1].split()[0], chosen_target_degree)
                            generation_method += ('\n\t' + __generation_method)

                        leading_targets.remove(chosen_target_degree)
            
            if candidate_chord is None:
                # Perform weighted coin toss to decide whether to use a common voicing
                use_chord_voicing_from_library = decide_will_event_occur(self.chance_to_use_voicing_from_library)
                if use_chord_voicing_from_library:
                    chosen_target_degree = random.choice(chord_charts[self.scale])
                    chord_root_note = roman_numeral_to_note(chosen_target_degree, allowed_notes)
                    if chord_root_note != -1:
                        built_chord, name_of_chord, name_of_voicing = self.build_chord_with_random_good_voicing(chosen_target_degree, chord_root_note)
                        if built_chord != -1:
                            candidate_chord = built_chord
                            name_of_candidate_chord = name_of_chord
                            generation_method = '\t- Decided to build a {} on a {}.'.format(name_of_voicing, chosen_target_degree)

            if candidate_chord is None:
                generation_method = '\t- Picked {} scale notes at random.'.format(num_notes_in_chord)
                candidate_chord = pick_n_random_notes(allowed_notes, num_notes_in_chord)
            
            # If the candidate chord fails user-applied constraints, regenerate it randomly.
            # Try to design the previous algorithms so that we avoid having to regenerate from random.
            # (I checked for accidentals during the voicing selection process)
            fails_repeats_constraint = self.disallow_repeats and chords_are_equal(previous_chord, candidate_chord)
            if self.disallow_repeats and fails_repeats_constraint:
                max_retries = 6
                retries = 0
                while fails_repeats_constraint and retries < max_retries:
                    retries += 1
                    num_notes_in_chord = random.choice(allowed_chord_sizes)
                    candidate_chord = pick_n_random_notes(allowed_notes, num_notes_in_chord)
                    generation_method = '\t- Picked {} scale notes at random.'.format(num_notes_in_chord)
                    fails_repeats_constraint = self.disallow_repeats and chords_are_equal(previous_chord, candidate_chord)
                    # fails_accidentals_constraint = (not self.allow_accidentals) and does_chord_contain_accidentals(candidate_chord, allowed_notes)

            result_chord_progression.append(candidate_chord)
            previous_chord = candidate_chord
            if name_of_candidate_chord is not None:
                previous_chord_name = name_of_candidate_chord
            else:
                previous_chord_name = determine_chord_name(flatten_note_set(candidate_chord), self.key, constants['scales'][self.scale])
            result_chord_names.append(previous_chord_name)
            
            previous_chord_degree = previous_chord_name[1].split()[0]
            degree = None
            try:
                degree = previous_chord_name[1].split()[0]
            except Exception as e:
                print('Exception: ', e)
                traceback.print_exception(*exc_info)
                pass
            ClientLogger.log('Added {} ( {} ). Generation pathway: \n{}'.format(previous_chord_name[0], degree, generation_method))
        
        return result_chord_progression, result_chord_names