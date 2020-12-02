import random
from constants import constants
from utils import roman_to_int, decide_will_event_occur, flatten_note_set, pick_n_random_notes, pretty_print_progression
from client_logging import ClientLogger
import midi_tools
import music_theory
from music_theory import determine_chord_name, get_allowed_notes, transpose_note_n_semitones
import sys, traceback
import json
from generator import Generator
ClientLogger = ClientLogger()

class MelodyGenerator(Generator):
    def __init__(self, content):
        super(MelodyGenerator, self).__init__(content)
 
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