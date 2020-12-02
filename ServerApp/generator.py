import random
from constants import constants
from utils import roman_to_int, decide_will_event_occur, flatten_note_set, pick_n_random_notes, pretty_print_progression
from client_logging import ClientLogger
import midi_tools
import music_theory
from music_theory import get_allowed_notes, transpose_note_n_semitones
import sys, traceback
import json
ClientLogger = ClientLogger()

class Generator:
    def __init__(self, content):
        generation_type = content['generationType']
        self.all_settings = ""
        for x in content.keys():
            self.all_settings += "\n\t" + x + ": " + str(content[x])
        self.key = content['key'].replace('#', 's').lower()
        self.scale = content['scale']
        self.scale_name = constants['scales'][self.scale]['name']
        self.length = content['length']
        self.disallow_repeats = content['disallowRepeats']
        self.octave_range = list(range(content['octaveLowerBound'], content['octaveUpperBound'] + 1))
        self.allowed_notes = get_allowed_notes(self.key, self.scale, self.octave_range)
        self.parent_scale_allowed_notes = self.allowed_notes
        self.parent_scale_code = self.scale
        self.contains_scale = self.scale
        self.parent_scale_allowed_notes = self.allowed_notes
        if len(constants['scales'][self.scale]['intervals']) < 7:
            self.parent_scale_code = constants['scales'][self.scale]['parent_scale']
            self.parent_scale_allowed_notes = get_allowed_notes(self.key, self.parent_scale_code, [3])
        if 'contains_scale' in constants['scales'][self.scale]:
            self.contains_scale = constants['scales'][self.scale]['contains_scale']
        self.track_number = content['trackNumber']
        # We measure "beats" in whole notes. Each chord is a whole note.
        self.current_beat = 0
