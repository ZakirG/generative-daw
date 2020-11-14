import random
from constants import constants
from chord_knowledge import chord_leading_chart, good_voicings, chord_charts, good_chord_progressions, chord_name_caches
from utils import roman_to_int, decide_will_event_occur, flatten_note_set, pick_n_random_notes, pretty_print_progression
from client_logging import ClientLogger
import midi_tools
import music_theory
from music_theory import determine_chord_name, get_allowed_notes, \
    transpose_note_n_semitones, build_chord_from_voicing, label_voicings_with_metadata, \
    roman_numeral_to_note, chords_are_equal, topline_note_passes_topline_constraints, non_topline_note_meets_topline_constraints, \
        chord_passes_topline_contour_constraint, convert_chord_to_cache_key
import sys, traceback
import json
from generator import Generator
ClientLogger = ClientLogger()

class ChordsGenerator(Generator):
    def __init__(self, content):
        super(ChordsGenerator, self).__init__(content)

        self.chance_to_use_chord_leading=content['chanceToUseChordLeadingChart']
        self.chance_to_use_voicing_from_library = content['chanceToUseCommonVoicing']
        chord_size_bounds = (content['chordSizeLowerBound'], content['chordSizeUpperBound'])
        self.chord_size_upper_bound = chord_size_bounds[1]
        self.chord_size_lower_bound = chord_size_bounds[0]
        
        # Account for cases where there are very few allowed notes in the scale (like a pentatonic scale)
        upper_bd = min(self.chord_size_upper_bound, len(self.allowed_notes))
        if upper_bd == self.chord_size_lower_bound:
            self.allowed_chord_sizes = [upper_bd]
        else:
            self.allowed_chord_sizes = range(self.chord_size_lower_bound, upper_bd + 1)

        self.chance_to_allow_non_diatonic_chord = content['chanceToAllowNonDiatonicChord']
        self.chance_to_allow_borrowed_chord = content['chanceToAllowBorrowedChord']
        self.chance_to_allow_alt_dom_chord = content['chanceToAllowAlteredDominantChord']
        self.chance_to_use_common_progression = content['chanceToUseCommonProgression']
        # Labeling chord voicings with acceptable roman numerals per scale to preserve diatonicity.
        # This result is specific to the scale of interest. But not its key.
        self.labeled_voicings = label_voicings_with_metadata(self.key, self.scale, self.octave_range)

        self.max_topline_distance = content["maxToplineDistance"]
        # self.note_changes_lower_bound = content["noteChangesLowerBound"]
        # self.note_changes_upper_bound= content["noteChangesUpperBound"]
        self.topline_contour = content["toplineContour"]
        # On each beat, the chord topline will need to respect a height constraint relative to the
        # previous chord.
        self.beats_to_contour_directions = music_theory.get_contour_directions_per_beat(self.topline_contour, self.length)

 
    def get_current_topline_direction(self):
        """
        The topline contour is a shape stretching over the progression time length.
        To achieve the user-provided topline contour,
        we must enforce a relative height constraint when choosing a chord relative to
        the previous chord.
        """
        return self.beats_to_contour_directions[self.current_beat]

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

    def build_chord_with_root_randomly(self, chord_root_note, chosen_target_degree, previous_chord):
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

        # As a rule, let's require the chord root and the third are in the chord.
        result_chord = [chord_root_note['note'], third_of_chord]
        extra_notes_to_add = []
        
        fifth_of_chord = transpose_note_n_semitones(chord_root_note['note'], 7)
        if is_diminished:
            # diminished chord
            fifth_of_chord = transpose_note_n_semitones(chord_root_note['note'], 6)
        elif is_augmented:
            # augmented chord
            fifth_of_chord = transpose_note_n_semitones(chord_root_note['note'], 8)
        extra_notes_to_add.append(fifth_of_chord)
        
        semitones_up_to_seventh = 11 # major seventh
        if is_diminished:
            semitones_up_to_seventh = 9
        elif is_augmented or quality == 'minor':
            semitones_up_to_seventh = 10
        seventh_of_chord = transpose_note_n_semitones(chord_root_note['note'], semitones_up_to_seventh)
        extra_notes_to_add.append(seventh_of_chord)
        
        # Diminished chords sound good with major ninths too
        semitones_up_to_ninth = 14
        if is_augmented:
            # Augmented sharp-nine chords sound cool
            semitones_up_to_ninth = 15
        ninth_of_chord = transpose_note_n_semitones(chord_root_note['note'], semitones_up_to_ninth)
        extra_notes_to_add.append(ninth_of_chord)

        # Avoiding major sharp 11ths for now. Sharp 11ths on a major chord are done in jazz, but my code doesn't yet support accidentals.
        # if quality == 'major':
        #   # Sharpened 11th for major chord
        #    eleventh_of_chord = transpose_note_n_semitones(chord_root_note['note'], 18)
        if quality == 'minor':
            eleventh_of_chord = transpose_note_n_semitones(chord_root_note['note'], 17)
            extra_notes_to_add.append(eleventh_of_chord)
        
        if quality == 'major':
            # 13th is the 6th
            sixth_of_chord = transpose_note_n_semitones(chord_root_note['note'], 9)
            extra_notes_to_add.append(sixth_of_chord)
        
        # Avoiding minor 13ths for now, because minor sixths chords usually sharpen to get a major sixth, 
        # and my code doesn't support accidentals yet.
        # if quality == 'minor':
        #     sixth_of_chord = transpose_note_n_semitones(chord_root_note['note'], 9)
        #     extra_notes_to_add.append(sixth_of_chord)

        # Filtering allowed notes by diatonicity
        reject_non_diatonic_chord =  decide_will_event_occur(1 - self.chance_to_allow_non_diatonic_chord)
        diatonic_letters = [x['note'] for x in self.allowed_notes]
        if reject_non_diatonic_chord:
            # Eliminate note choices outside of the self.key.
            extra_notes_to_add = [x for x in extra_notes_to_add if x in diatonic_letters]

        note_choices_all_octaves = []
        for octave in self.octave_range:
            note_choices_all_octaves += list(map(lambda x: {'note': x, 'octave': octave}, extra_notes_to_add))
        
        extra_notes_to_add = note_choices_all_octaves.copy()
        previous_chord_topline_position = None
        if previous_chord is not None and len(previous_chord) > 0:
            previous_chord_topline_position = music_theory.chord_to_topline_int(previous_chord)

        try:
            required_topline_note, extra_notes_to_add = self.select_notes_that_satisfy_topline_constraints(extra_notes_to_add, previous_chord)
        except Exception:
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)
            return -1

        result_chord = [ {'note': x, 'octave': y} for x in result_chord for y in self.octave_range]
        required_non_topline_notes = []
        for x in result_chord:
            if non_topline_note_meets_topline_constraints(self.get_current_topline_direction(), x, previous_chord_topline_position, self.max_topline_distance):
                required_non_topline_notes.append(x)

        # Make sure we try to get one of each of the (non-topline) required notes (usually the root and the third)
        # required_non_topline_notes_all_octaves = set([ {x['note'] for x in result_chord_filtered_by_topline_constraint ])
        # required_non_topline_notes = []
        # octave_to_note = {}
        # for x in required_non_topline_notes_all_octaves:
        #     if x['octave'] not in octave_to_note:
        #         octave_to_note[x['octave']] = [x]
        #     else:
        #         octave_to_note[x['octave']].append(x)
        # for key in octave_to_note.keys():
        #     required_non_topline_notes.append(random.choice(octave_to_note[key]))


        max_chord_size = len(extra_notes_to_add) + len(required_non_topline_notes) + len(required_topline_note)
        if max_chord_size < self.chord_size_lower_bound:
            # Not enough notes in the scale to build a decent chord on this root.
            return -1
        
        chord_size = min(random.choice(self.allowed_chord_sizes), max_chord_size)
        if reject_non_diatonic_chord:
            chord_size = min(chord_size, len(diatonic_letters))
        
        result_chord = required_topline_note + pick_n_random_notes(required_non_topline_notes, min(len(required_non_topline_notes), chord_size - 1)) 
        result_chord += pick_n_random_notes(extra_notes_to_add, (chord_size - len(result_chord)))
        # Verify that we meet the topline constraint
        candidate_topline_position = music_theory.chord_to_topline_int(result_chord)
        if previous_chord is not None and len(previous_chord) > 0:
            topline_distance = abs(previous_chord_topline_position - candidate_topline_position)
            if topline_distance > self.max_topline_distance:
                # We tried to get as close as possible, but we failed the topline constraint.
                return -1

        return result_chord

    def voicing_on_numeral_passes_constraints(self, voicing, voicing_group_quality, chosen_target_degree, chord_root_note, previous_chord, previous_chord_topline_position):
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
            allowed_qualities = ['major', 'dominant-7', 'sus']
        else:
            allowed_qualities = ['minor', 'sus']
        # elif chosen_target_degree == 'v' and self.chance_to_allow_non_diatonic_chord > 0:
        #     # V Dominant 7 chords are sometimes borrowed for use in a minor context
        #     # Contains an accidental, from the harmonic minor
        #     voicings_for_quality = self.labeled_voicings['minor'] + self.labeled_voicings['dominant-7']
        # elif chosen_target_degree == 'iv' and self.allow_accidentals:
        #     The Neapolitan chord https://www.youtube.com/watch?v=K8Z6MTonoXE&ab_channel=MusicTheoryForGuitar

        chord_size = len(voicing['intervals']) + 1
        candidate_metadata = voicing['roman_numerals_to_metadata'][chosen_target_degree]

        passes_chord_size_constraint = (chord_size >= self.chord_size_lower_bound and chord_size <= self.chord_size_upper_bound)
        # Whether this voicing will fit on this scale degree has been precalculated.
        passes_octave_constraint = candidate_metadata["it_fits_in_the_octave_range"]
        passes_diatonicity_constraint = True

        
        candidate_chord = build_chord_from_voicing(voicing, chord_root_note, chosen_target_degree, self.octave_range)
        passes_repeats_constraint = not self.disallow_repeats or not chords_are_equal(previous_chord, candidate_chord)

        reject_non_diatonic_chord =  decide_will_event_occur(1 - self.chance_to_allow_non_diatonic_chord)
        allow_borrowed_chord = decide_will_event_occur(self.chance_to_allow_borrowed_chord)
        allow_alt_dom_chord = decide_will_event_occur(self.chance_to_allow_alt_dom_chord)

        chord_is_non_diatonic = candidate_metadata['it_contains_accidentals']
        chord_is_borrowed = voicing_group_quality not in allowed_qualities and (voicing_group_quality == 'major' or voicing_group_quality == 'minor')
        chord_is_alt_dom = chosen_target_degree == 'V' and voicing_group_quality == 'dominant-7' and chord_is_non_diatonic
        
        bypass_diatonicity_constraint_because_chord_is_borrowed = chord_is_borrowed and allow_borrowed_chord
        bypass_diatonicity_constraint_because_chord_is_alt_dom = chord_is_alt_dom and allow_alt_dom_chord
        bypass_diatonicity_constraint = bypass_diatonicity_constraint_because_chord_is_borrowed or bypass_diatonicity_constraint_because_chord_is_alt_dom
        
        """
        self.chance_to_allow_non_diatonic_chord should be independent of self.allow_borrowed_chord. If the allow non-diatonic chord diceroll succeeded,
        but the allow_borrowed_chord diceroll failed and this is a borrowed chord, DO NOT allow a borrowed chord.
        """
        if (chord_is_non_diatonic and reject_non_diatonic_chord and not bypass_diatonicity_constraint) \
            or (chord_is_borrowed and not bypass_diatonicity_constraint):
            passes_diatonicity_constraint = False
        
        candidate_topline_position = candidate_metadata['topline_position']
        passes_topline_constraints = topline_note_passes_topline_constraints(self.get_current_topline_direction(), candidate_topline_position, previous_chord_topline_position, self.max_topline_distance)
        passes_constraints = passes_chord_size_constraint and passes_octave_constraint and passes_repeats_constraint and passes_diatonicity_constraint and passes_topline_constraints
        return passes_constraints, chord_is_borrowed, chord_is_alt_dom, chord_is_non_diatonic, candidate_chord

    def build_chord_with_random_good_voicing(self, chosen_target_degree, chord_root_note, previous_chord):
        """
        Returns (built_chord, [chord_letter_name, chord_roman_name], chosen_voicing['name'])
        """
        
        previous_chord_topline_position = None
        if previous_chord is not None and len(previous_chord) > 0:
            previous_chord_topline_position = music_theory.chord_to_topline_int(previous_chord)
        applicable_voicings = []
        for voicing_group_quality in self.labeled_voicings.keys():
            voicing_group = self.labeled_voicings[voicing_group_quality]
            for voicing in voicing_group:
                passes_constraints, is_borrowed, is_alt_dom, is_non_diatonic, built_chord = self.voicing_on_numeral_passes_constraints(voicing, voicing_group_quality, chosen_target_degree, chord_root_note, previous_chord, previous_chord_topline_position)
                if passes_constraints:
                    voicing_copy = voicing.copy()
                    voicing_copy['quality'] = voicing_group_quality
                    voicing_copy['is_borrowed'] = is_borrowed
                    voicing_copy['is_alt_dom'] = is_alt_dom
                    voicing_copy['is_non_diatonic'] = is_non_diatonic
                    voicing_copy['built_chord'] = built_chord
                    applicable_voicings.append(voicing_copy)
        
        if len(applicable_voicings) > 0:
            chosen_voicing = random.choice(applicable_voicings)
            built_chord = chosen_voicing['built_chord']
            chord_letter_name = chord_root_note['note'].upper().replace('S', '#') + ' ' + chosen_voicing['name']
            
            # Must recalculate degree here, as a borrowed chord may have been used.
            recalculated_degree = chosen_target_degree
            if chosen_voicing['quality'] == 'major':
                recalculated_degree = recalculated_degree.upper()
            if chosen_voicing['quality'] == 'minor':
                recalculated_degree = recalculated_degree.lower()
            chord_roman_name = recalculated_degree + ' ' + chosen_voicing['name']
            
            generation_method = ''
            if chosen_voicing['is_borrowed']:
                generation_method += "\n\t- Decided to allow a borrowed chord."
            elif chosen_voicing['is_alt_dom']:
                generation_method += "\n\t- Decided to allow a non-diatonic altered dominant chord."
            elif chosen_voicing['is_non_diatonic']:
                generation_method += "\n\t- Decided to allow a non-diatonic chord."
            generation_method += "\n\t- Chose to voice {} as a {} from {} applicable voicings.".format(chosen_target_degree, chosen_voicing['name'], len(applicable_voicings))
            return built_chord, [chord_letter_name, chord_roman_name], generation_method
        return -1, -1, -1

    def build_chord_from_roman_numeral(self, chosen_target_degree, previous_chord):
        """
        Returns (built_chord, name_of_chord, generation_method)
        """
        chord_root_note = roman_numeral_to_note(chosen_target_degree, self.parent_scale_allowed_notes)

        # Perform weighted coin toss
        use_chord_voicing_from_library = decide_will_event_occur(self.chance_to_use_voicing_from_library)

        if use_chord_voicing_from_library:
            # First, lets filter the voicings library down to match the chord size and roman numeral constraints.
            built_chord, name_of_chord, generation_method = self.build_chord_with_random_good_voicing(chosen_target_degree, chord_root_note, previous_chord)
            if built_chord != -1:
                return (built_chord, name_of_chord, generation_method)

        # If all else fails, build it randomly.
        built_chord = self.build_chord_with_root_randomly(chord_root_note, chosen_target_degree, previous_chord)
        generation_method = '\n\t- Built {} by picking chord tones at random.'.format(chosen_target_degree)
        name_of_chord = None
        if built_chord != -1:
            name_of_chord = determine_chord_name(flatten_note_set(built_chord), self.key, constants['scales'][self.scale])
        return (built_chord, name_of_chord, generation_method)

    def chord_fails_topline_distance_constraint(self, candidate_chord, previous_chord):
        return previous_chord is not None and len(previous_chord) > 0 and (music_theory.calculate_topline_distance(previous_chord, candidate_chord) > self.max_topline_distance)
    
    def chord_fails_topline_contour_constraint(self, candidate_chord, previous_chord):
        if self.topline_contour['code'] == "any" or previous_chord is None or len(previous_chord) == 0:
            return False
        return not chord_passes_topline_contour_constraint(self.get_current_topline_direction(), music_theory.chord_to_topline_int(candidate_chord), music_theory.chord_to_topline_int(previous_chord))

    def select_notes_that_satisfy_topline_constraints(self, allowed_notes, previous_chord):
        required_notes_in_chord = []
        previous_chord_topline_position = music_theory.chord_to_topline_int(previous_chord)
        note_choices_to_add_to_chord = allowed_notes.copy()
        # Pre-select candidates for topline notes and require the chord to have one of them.
        allowed_highest_notes = []
        for note in allowed_notes:
            note_pos = midi_tools.note_to_numeral(note)
            if topline_note_passes_topline_constraints(self.get_current_topline_direction(), note, previous_chord_topline_position, self.max_topline_distance):
                allowed_highest_notes.append(note)

        highest_note_choice = random.choice(allowed_highest_notes)
        highest_note_index = note_choices_to_add_to_chord.index(highest_note_choice)
        # Remove that note from the remaining choices.
        note_choices_to_add_to_chord = note_choices_to_add_to_chord[:highest_note_index] + note_choices_to_add_to_chord[highest_note_index+1:]
        required_notes_in_chord.append(highest_note_choice)

        # Remove notes from candidates that would violate the topline constraints from above
        note_choices_to_add_to_chord_filtered = []
        for note in note_choices_to_add_to_chord:
            passes_topline_constraints = non_topline_note_meets_topline_constraints(self.get_current_topline_direction(), note, previous_chord_topline_position, self.max_topline_distance)
            if self.get_current_topline_direction() == 'unequal' and midi_tools.note_to_numeral(note) == previous_chord_topline_position:
                continue
            if passes_topline_constraints:
                note_choices_to_add_to_chord_filtered.append(note)
        note_choices_to_add_to_chord = note_choices_to_add_to_chord_filtered
        return required_notes_in_chord, note_choices_to_add_to_chord

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
                    leading_chord, name_of_chord, __generation_method = self.build_chord_from_roman_numeral(chosen_target_degree, previous_chord)
                
                    if leading_chord != -1:
                        candidate_chord = leading_chord
                        name_of_candidate_chord = name_of_chord
                        generation_method = '\t- Used {} chord leading chart suggestion {} -> {}. '.format(quality, previous_chord_name[1].split()[0], chosen_target_degree)
                        generation_method += __generation_method

                    leading_targets.remove(chosen_target_degree)
        
        if candidate_chord is None:
            # Pick a random degree of the scale and build a chord on it
            chosen_target_degree = random.choice(chord_charts[self.scale])
            built_chord, name_of_chord, __generation_method = self.build_chord_from_roman_numeral(chosen_target_degree, previous_chord)
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
        fails_repeats_constraint = self.disallow_repeats and chords_are_equal(previous_chord, candidate_chord)
        fails_topline_distance_constraint = self.chord_fails_topline_distance_constraint(candidate_chord, previous_chord)
        fails_topline_contour_constraint = self.chord_fails_topline_contour_constraint(candidate_chord, previous_chord)
        
        required_notes_in_chord = []
        extra_notes = self.allowed_notes
        if fails_topline_distance_constraint or fails_topline_contour_constraint:
            try:       
                required_notes_in_chord, extra_notes = self.select_notes_that_satisfy_topline_constraints(self.allowed_notes, previous_chord)
            except Exception:
                exc_info = sys.exc_info()
                traceback.print_exception(*exc_info)
        
        max_retries = 20
        retries = 0
        # If we run out of retries, we'll just have to violate the constraint. There are no other generation algorithms after this one.
        while (fails_repeats_constraint or fails_topline_distance_constraint or fails_topline_contour_constraint) and retries < max_retries:
            retries += 1
            allowed_chord_sizes = list(self.allowed_chord_sizes).copy()
            if fails_repeats_constraint and len(allowed_chord_sizes) > 1:
                # Lets forcibly pick a different number of chord tones.
                index = allowed_chord_sizes.index(len(previous_chord))
                allowed_chord_sizes.pop(index)
            num_notes_in_chord = random.choice(allowed_chord_sizes)
            num_notes_to_pick = min(num_notes_in_chord - len(required_notes_in_chord), len(extra_notes))
            candidate_chord = pick_n_random_notes(extra_notes, num_notes_to_pick) + required_notes_in_chord
            generation_method = '\t- Picked {} scale notes at random.'.format(num_notes_in_chord)
            fails_repeats_constraint = self.disallow_repeats and chords_are_equal(previous_chord, candidate_chord)
            fails_topline_distance_constraint = self.chord_fails_topline_distance_constraint(candidate_chord, previous_chord)
            fails_topline_contour_constraint = self.chord_fails_topline_contour_constraint(candidate_chord, previous_chord)
            # fails_accidentals_constraint = (not self.allow_accidentals) and does_chord_contain_accidentals(candidate_chord, self.allowed_notes)

        if retries == max_retries and fails_repeats_constraint:
            ClientLogger.log('Error: After {} retries, the disallow repeats constraint could not be satisfied.'.format(retries))
        if retries == max_retries and fails_topline_distance_constraint:
            ClientLogger.log('Error: After {} retries, the topline distance constraint could not be satisfied.'.format(retries))
        if retries == max_retries and fails_topline_contour_constraint:
            ClientLogger.log('Error: After {} retries, the topline contour constraint could not be satisfied.'.format(retries))

        if name_of_candidate_chord is None:
            name_of_candidate_chord = determine_chord_name(flatten_note_set(candidate_chord), self.key, constants['scales'][self.scale])
        
        try:
            degree_of_candidate_chord = name_of_candidate_chord[1].split()[0]
        except Exception as e:
            degree_of_candidate_chord = '?'
            print('Failed to name chord. Exception: ', e)
            exc_info = sys.exc_info()
            traceback.print_exception(*exc_info)
        
        return candidate_chord, name_of_candidate_chord, degree_of_candidate_chord, generation_method

    def materialize_chord_progression(self, progression, previous_chord, previous_chord_degree):
        progression_str = pretty_print_progression(progression['roman_numerals'])
        progression_chords = []
        prev_chord = previous_chord
        progression_chord_names = []
        beat_before_progression_starts = self.current_beat
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
            self.current_beat += 1
            chord, chord_name, __generation_method = self.build_chord_from_roman_numeral(numeral_to_add, prev_chord)
            if chord == -1:
                print('Failed to build chord on ', numeral_to_add)
                # Reset the beat and backtrack. This line is not strictly necessary, as the beat will be reset in the outer loop
                # anyway. But for completeness and readability I reset it here explicitly.
                self.current_beat = beat_before_progression_starts
                # Exit early because we failed to build one of the chords without violating constraints.
                return None, None, None
            generation_method = '\t- Using {} to satisfy the {}.'.format(numeral_to_add, progression_str)
            generation_method += __generation_method
            progression_chords.append(chord)
            progression_chord_names.append(chord_name)
            lines_to_log.append('Added {} ( {} ). Generation pathway: \n{}'.format(chord_name[0], numeral_to_add, generation_method))
            prev_chord = chord
        return progression_chords, progression_chord_names, lines_to_log
    
    def generate_chords(self):
        ClientLogger.log('Generating new chord progression in {} {}.'.format(self.key.upper(), self.scale_name))
        result_chord_progression = []
        result_chord_names = []
        previous_chord = []
        previous_chord_degree = '?'
        previous_chord_name = '', ''
        
        while len(result_chord_progression) < self.length:
            # We measure "beats" in whole notes. Each chord is a whole note.
            self.current_beat = len(result_chord_progression)

            # Perform weighted coin toss to use a pre-selected chord progression
            use_chord_progression_from_library = decide_will_event_occur(self.chance_to_use_common_progression)
            # Which chord progressions fit in the remaining space?
            allowed_progressions = []
            for progression in good_chord_progressions[self.parent_scale_code]:
                if len(progression['roman_numerals']) + len(result_chord_progression) < self.length:
                    allowed_progressions.append(progression)
            
            
            if use_chord_progression_from_library and len(allowed_progressions) > 0:
                progression = random.choice(allowed_progressions)
                progression_chords, progression_chord_names, lines_to_log = self.materialize_chord_progression(progression, previous_chord, previous_chord_degree)
                if progression_chords is None:
                    continue
                
                result_chord_progression += progression_chords
                result_chord_names += progression_chord_names
                previous_chord = result_chord_progression[-1]
                previous_chord_name = result_chord_names[-1]
                previous_chord_degree = progression['roman_numerals'][-1]
                
                for line in lines_to_log:
                    ClientLogger.log(line)
                progression_str = pretty_print_progression(progression['roman_numerals'])
                ClientLogger.log('{} progression complete.'.format(progression_str))
            else:
                chord, chord_name, chord_degree, generation_method = self.generate_next_chord(previous_chord, previous_chord_degree, previous_chord_name)
                result_chord_progression.append(chord)
                result_chord_names.append(chord_name)

                previous_chord = chord
                previous_chord_name = chord_name
                previous_chord_degree = chord_degree
                
                ClientLogger.log('Added {} ( {} ). Generation pathway: \n{}'.format(previous_chord_name[0], previous_chord_degree, generation_method))
        
        ClientLogger.log('~~~')
        ClientLogger.log('Generation settings: {}'.format(self.all_settings))

        result_chord_progression_labeled_with_midi_numerals = []
        for i in range(len(result_chord_progression)):
            chord = result_chord_progression[i]
            labeled_chord = []
            for note in chord:
                note['numeral'] = midi_tools.note_to_numeral(note)
                labeled_chord.append(note)
            result_chord_progression_labeled_with_midi_numerals.append(labeled_chord)
        
            cache_key = convert_chord_to_cache_key(chord)
            chord_name_caches[self.track_number][cache_key] = result_chord_names[i]
        
        return result_chord_progression_labeled_with_midi_numerals, result_chord_names