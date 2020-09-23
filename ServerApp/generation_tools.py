import random
from constants import constants
from chord_knowledge import chord_leading_chart, good_voicings, chord_charts, good_chord_progressions
from utils import roman_to_int, decide_will_event_occur, flatten_note_set, pick_n_random_notes, pretty_print_progression
from client_logging import ClientLogger
from music_theory import determine_chord_name, get_allowed_notes, \
    transpose_note_n_semitones, build_chord_from_voicing, label_voicings_by_roman_numeral, \
    roman_numeral_to_note, chords_are_equal
import sys, traceback
ClientLogger = ClientLogger()

class Generator:
    def __init__(self, content):
        generation_type = content['generationType']

        self.key = content['key'].replace('#', 's').lower()
        self.scale = content['scale']
        self.scale_name = constants['scales'][self.scale]['name']
        self.length = content['length']
        self.disallow_repeats = content['disallowRepeats']
        self.octave_range = list(range(content['octaveLowerBound'], content['octaveUpperBound'] + 1))
        self.allowed_notes = get_allowed_notes(self.key, self.scale, self.octave_range)
        self.parent_scale_allowed_notes = self.allowed_notes
        if len(constants['scales'][self.scale]['intervals']) < 7:
            self.parent_scale_code = constants['scales'][self.scale]['parent_scale']
            self.parent_scale_allowed_notes = get_allowed_notes(self.key, parent_scale_code, [3])

        if generation_type == 'chords':
            self.chance_to_use_chord_leading=content['chanceToUseChordLeadingChart']
            self.chance_to_use_voicing_from_library = content['chanceToUseCommonVoicing']
            chord_size_bounds = (content['chordSizeLowerBound'], content['chordSizeUpperBound'])
            self.chord_size_upper_bound = chord_size_bounds[1]
            self.chord_size_lower_bound = chord_size_bounds[0]
            self.chance_to_allow_non_diatonic_chord = content['chanceToAllowNonDiatonicChord']
            self.chance_to_allow_borrowed_chord = content['chanceToAllowBorrowedChord']
            self.chance_to_allow_alt_dom_chord = content['chanceToAllowAlteredDominantChord']
            self.chance_to_use_common_progression = content['chanceToUseCommonProgression']
            # Labeling chord voicings with acceptable roman numerals per scale to preserve diatonicity.
            # This result is specific to the scale of interest. But not its key.
            self.labeled_voicings = label_voicings_by_roman_numeral(self.key, self.scale)
            # Account for cases where there are very few allowed notes in the scale (like a pentatonic scale)
            upper_bd = min(self.chord_size_upper_bound, len(self.allowed_notes))
            self.allowed_chord_sizes = range(self.chord_size_lower_bound, upper_bd + 1)
            if upper_bd == self.chord_size_lower_bound:
                self.allowed_chord_sizes = [upper_bd]
 
    def generate_melody(self):
        result = []
        previous_note = None
        for i in range(self.length):
            candidate_note = random.choice(self.allowed_notes)
            # If repeats are disallowed, allow up to 6 retries to find a different noteset.
            if self.disallow_repeats and previous_note is not None:
                max_retries = 6
                retries = 0
                while set(flatten_note_set([previous_note])) == set(flatten_note_set([candidate_note])) and retries < max_retries:
                    retries += 1
                    candidate_note = random.choice(self.allowed_notes)

            result.append([candidate_note])
            previous_note = candidate_note
        
        return result

    def build_chord_with_root_randomly(self, chord_root_note, chosen_target_degree):
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

        # Eliminate note choices outside of the self.key.
        allowed_letters = [x['note'] for x in self.allowed_notes]
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
        
        allowed_qualities = []
        # if chosen_target_degree == 'V' and self.v_must_be_dom_7:
        #     allowed_qualities = ['dominant-7']
        # if chosen_target_degree == 'V': # and not self.v_must_be_dom_7:
        #     allowed_qualities = ['dominant-7', 'major']
        if '\xB0' in chosen_target_degree:
            allowed_qualities = ['diminished']
        elif '+' in chosen_target_degree and chosen_target_degree.isupper():
            allowed_qualities = ['augmented']
        elif chosen_target_degree.isupper():
            allowed_qualities = ['major', 'dominant-7']
        else:
            allowed_qualities = ['minor']
        # elif chosen_target_degree == 'v' and self.chance_to_allow_non_diatonic_chord > 0:
        #     # V Dominant 7 chords are sometimes borrowed for use in a minor context
        #     # Contains an accidental, from the harmonic minor
        #     voicings_for_quality = self.labeled_voicings['minor'] + self.labeled_voicings['dominant-7']
        # elif chosen_target_degree == 'iv' and self.allow_accidentals:
        #     The Neapolitan chord https://www.youtube.com/watch?v=K8Z6MTonoXE&ab_channel=MusicTheoryForGuitar
        
        applicable_voicings = []
        for voicing_group_quality in self.labeled_voicings.keys():
            voicing_group = self.labeled_voicings[voicing_group_quality]
            for voicing in voicing_group:
                chord_size = len(voicing['intervals']) + 1
                matches_chord_size_constraint = (chord_size >= self.chord_size_lower_bound and chord_size <= self.chord_size_upper_bound)
                matches_octave_constraint = True # TODO
                matches_diatonicity_constraint = True

                # TODO: add exceptions here, if configured by the user, for specific non-diatonic techniques (like 
                # allowing altered notes in dominants)
                # Perform weighted coin-toss: will we allow a non-diatonic chord?
                # Technically, this configuration option is misleadingly named. It's not the
                # chance to allow a non-diatonic chord, it's the chance to not reject a chord
                # for being non-diatonic.
                reject_non_diatonic_chord =  decide_will_event_occur(1 - self.chance_to_allow_non_diatonic_chord)
                allow_borrowed_chord = decide_will_event_occur(self.chance_to_allow_borrowed_chord)
                allow_alt_dom_chord = decide_will_event_occur(self.chance_to_allow_alt_dom_chord)

                chord_is_non_diatonic = chosen_target_degree not in voicing['allowed_roman_numerals']
                chord_is_borrowed = voicing_group_quality not in allowed_qualities and (voicing_group_quality == 'major' or voicing_group_quality == 'minor')
                chord_is_alt_dom = chosen_target_degree == 'V' and voicing_group_quality == 'dominant-7' and chord_is_non_diatonic
                
                bypass_diatonicity_constraint_because_chord_is_borrowed = chord_is_borrowed and allow_borrowed_chord
                bypass_diatonicity_constraint_because_chord_is_alt_dom = chord_is_alt_dom and allow_alt_dom_chord
                bypass_diatonicity_constraint = bypass_diatonicity_constraint_because_chord_is_borrowed or bypass_diatonicity_constraint_because_chord_is_alt_dom
                
                """
                This logic is a little complex, but the idea is -- self.chance_to_allow_non_diatonic_chord should be
                independent of self.allow_borrowed_chord. If the allow non-diatonic chord diceroll succeeded,
                but the allow_borrowed_chord diceroll failed and this is a borrowed chord, DO NOT allow a borrowed chord.
                """
                if (chord_is_non_diatonic and reject_non_diatonic_chord and not bypass_diatonicity_constraint) \
                    or (chord_is_borrowed and not bypass_diatonicity_constraint):
                    matches_diatonicity_constraint = False
                
                if matches_chord_size_constraint and matches_octave_constraint and matches_diatonicity_constraint:
                    voicing_copy = voicing.copy()
                    voicing_copy['quality'] = voicing_group_quality
                    voicing_copy['is_borrowed'] = chord_is_borrowed
                    voicing_copy['is_alt_dom'] = chord_is_alt_dom
                    voicing_copy['is_non_diatonic'] = chord_is_non_diatonic
                    applicable_voicings.append(voicing_copy)
        
        if len(applicable_voicings) > 0:
            chosen_voicing = random.choice(applicable_voicings)
            built_chord = build_chord_from_voicing(chosen_voicing, chord_root_note, chosen_target_degree, self.octave_range)
            chord_letter_name = chord_root_note['note'].upper().replace('S', '#') + ' ' + chosen_voicing['name']
            
            # Must recalculate degree here, as a borrowed chord may have been used.
            recalculated_degree = chosen_target_degree
            if chosen_voicing['quality'] == 'major':
                recalculated_degree = recalculated_degree.upper()
            if chosen_voicing['quality'] == 'minor':
                recalculated_degree = recalculated_degree.lower()
            chord_roman_name = recalculated_degree + ' ' + chosen_voicing['name']
            is_non_diatonic = chosen_voicing['is_non_diatonic']
            is_borrowed = chosen_voicing['is_borrowed']
            is_alt_dom = chosen_voicing['is_alt_dom']
            return built_chord, [chord_letter_name, chord_roman_name], chosen_voicing['name'], is_non_diatonic, is_borrowed, is_alt_dom
        return -1, -1, -1, -1, -1, -1

    def build_chord_from_roman_numeral(self, chosen_target_degree):
        """
        Returns (built_chord, name_of_chord, generation_method)
        """
        chord_root_note = roman_numeral_to_note(chosen_target_degree, self.parent_scale_allowed_notes)

        # Perform weighted coin toss
        use_chord_voicing_from_library = decide_will_event_occur(self.chance_to_use_voicing_from_library)

        if use_chord_voicing_from_library:
            # First, lets filter the voicings library down to match the chord size and roman numeral constraints.
            built_chord, name_of_chord, name_of_voicing, is_non_diatonic, is_borrowed, is_alt_dom = self.build_chord_with_random_good_voicing(chosen_target_degree, chord_root_note)
            if built_chord != -1:
                generation_method = ''
                if is_borrowed:
                    generation_method += "\n\t- Decided to allow a borrowed chord."
                elif is_alt_dom:
                    generation_method += "\n\t- Decided to allow a non-diatonic altered dominant chord."
                elif is_non_diatonic:
                    generation_method += "\n\t- Decided to allow a non-diatonic chord."
                generation_method += "\n\t- Decided to voice {} as a {}.".format(chosen_target_degree, name_of_voicing)
                return (built_chord, name_of_chord, generation_method)

        # If all else fails, build it randomly.
        built_chord = self.build_chord_with_root_randomly(chord_root_note, chosen_target_degree)
        generation_method = '\n\t- Built {} by picking chord tones at random.'.format(chosen_target_degree)
        name_of_chord = None
        if built_chord != -1:
            name_of_chord = determine_chord_name(flatten_note_set(built_chord), self.key, constants['scales'][self.scale])
        return (built_chord, name_of_chord, generation_method)

    def generate_next_chord(self, previous_chord, previous_chord_degree, previous_chord_name):
        """
        Returns (chord, chord_name, chord_degree, generation_method)
        """
        num_notes_in_chord = random.choice(self.allowed_chord_sizes)
        candidate_chord = None
        name_of_candidate_chord = None
        degree_of_candidate_chord = None
        generation_method = ''

        # Perform weighted coin toss to use a chord leading chart
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
                    leading_chord, name_of_chord, __generation_method = self.build_chord_from_roman_numeral(chosen_target_degree)
                
                    if leading_chord != -1:
                        candidate_chord = leading_chord
                        name_of_candidate_chord = name_of_chord
                        generation_method = '\t- Used {} chord leading chart suggestion {} -> {}. '.format(quality, previous_chord_name[1].split()[0], chosen_target_degree)
                        generation_method += __generation_method

                    leading_targets.remove(chosen_target_degree)
        
        if candidate_chord is None:
            # Pick a random degree of the scale and build a chord on it
            chosen_target_degree = random.choice(chord_charts[self.scale])
            built_chord, name_of_chord, __generation_method = self.build_chord_from_roman_numeral(chosen_target_degree)
            if built_chord != -1:
                candidate_chord = built_chord
                name_of_candidate_chord = name_of_chord
                generation_method = '\t- Picked scale degree {} randomly.'.format(chosen_target_degree)
                generation_method += __generation_method

        if candidate_chord is None:
            generation_method = '\t- Picked {} scale notes at random.'.format(num_notes_in_chord)
            candidate_chord = pick_n_random_notes(self.allowed_notes, num_notes_in_chord)
        
        # If the candidate chord fails user-applied constraints, regenerate it randomly.
        # Try to design the previous algorithms so that we avoid having to regenerate from random.
        # (I checked for accidentals during the voicing selection process)
        fails_repeats_constraint = self.disallow_repeats and chords_are_equal(previous_chord, candidate_chord)
        max_retries = 6
        retries = 0
        while fails_repeats_constraint and retries < max_retries:
            retries += 1
            num_notes_in_chord = random.choice(self.allowed_chord_sizes)
            candidate_chord = pick_n_random_notes(self.allowed_notes, num_notes_in_chord)
            generation_method = '\t- Picked {} scale notes at random.'.format(num_notes_in_chord)
            fails_repeats_constraint = self.disallow_repeats and chords_are_equal(previous_chord, candidate_chord)
            # fails_accidentals_constraint = (not self.allow_accidentals) and does_chord_contain_accidentals(candidate_chord, self.allowed_notes)

        if name_of_candidate_chord is None:
            name_of_candidate_chord = determine_chord_name(flatten_note_set(candidate_chord), self.key, constants['scales'][self.scale])
        
        try:
            degree_of_candidate_chord = name_of_candidate_chord[1].split()[0]
        except Exception as e:
            degree_of_candidate_chord = '?'
            print('Exception: ', e)
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)
        
        return candidate_chord, name_of_candidate_chord, degree_of_candidate_chord, generation_method

    def generate_chords(self):
        result_chord_progression = []
        result_chord_names = []
        previous_chord = []
        previous_chord_degree = '?'
        previous_chord_name = '', ''
        while len(result_chord_progression) < self.length:
            # Perform weighted coin toss to use a pre-selected chord progression
            use_chord_progression_from_library = decide_will_event_occur(self.chance_to_use_common_progression)
            # Which chord progressions fit in the remaining space?
            allowed_progressions = []
            for progression in good_chord_progressions[self.scale_name]:
                if len(progression['roman_numerals']) + len(result_chord_progression) < self.length:
                    allowed_progressions.append(progression)
            
            if use_chord_progression_from_library and len(allowed_progressions) > 0:
                progression = random.choice(allowed_progressions)
                progression_str = pretty_print_progression(progression['roman_numerals'])
                progression_chords = []
                progression_chord_names = []
                # Log at the end only if everything is successful
                if len(progression['name']) > 0:
                    lines_to_log = ['Decided to incorporate {}. ({})'.format(progression_str, progression['name'])]
                else:
                    lines_to_log = ['Decided to incorporate {} progression.'.format(progression_str)]
                failure = False

                # If the first chosen progression happens to start on the same roman numeral as the previous
                # chord, lets skip that chord.
                remaining_numerals = progression['roman_numerals']
                if remaining_numerals[0] == previous_chord_degree:
                    remaining_numerals = remaining_numerals[1:]
                    lines_to_log += ["The previous chord was a {}, so we'll start the progression from {}.".format(previous_chord_degree, remaining_numerals[0])]

                for numeral_to_add in remaining_numerals:
                    chord, chord_name, __generation_method = self.build_chord_from_roman_numeral(numeral_to_add)
                    if chord == -1:
                        print('Failed to build chord on ', numeral_to_add)
                        failure = True
                        break
                    generation_method = '\t- Using {} to satisfy the {}.'.format(numeral_to_add, progression_str)
                    generation_method += __generation_method
                    progression_chords.append(chord)
                    progression_chord_names.append(chord_name)
                    lines_to_log.append('Added {} ( {} ). Generation pathway: \n{}'.format(chord_name[0], numeral_to_add, generation_method))
                if failure:
                    continue
                result_chord_progression += progression_chords
                result_chord_names += progression_chord_names
                previous_chord = result_chord_progression[-1]
                previous_chord_name = result_chord_names[-1]
                previous_chord_degree = progression['roman_numerals'][-1]
                for line in lines_to_log:
                    ClientLogger.log(line)
                ClientLogger.log('{} progression completed.'.format(progression_str))
            else:
                chord, chord_name, chord_degree, generation_method = self.generate_next_chord(previous_chord, previous_chord_degree, previous_chord_name)
                result_chord_progression.append(chord)
                result_chord_names.append(chord_name)

                previous_chord = chord
                previous_chord_name = chord_name
                previous_chord_degree = chord_degree
                
                ClientLogger.log('Added {} ( {} ). Generation pathway: \n{}'.format(previous_chord_name[0], previous_chord_degree, generation_method))
        
        return result_chord_progression, result_chord_names