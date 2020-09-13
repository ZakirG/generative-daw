from flask import Flask, render_template, send_from_directory
from flask import request, send_file
from flask_cors import CORS
import os
import json
from crossdomain import crossdomain
import constants
import generation_tools
from music_theory import name_chords_in_tracks
import midi_tools
from client_logging import ClientLogger
from generation_tools import Generator
app = Flask(__name__)
CORS(app)

BASE_URL = os.path.abspath(os.path.dirname(__file__))
CLIENT_APP_FOLDER = os.path.join(BASE_URL, "ClientApp")

DawState = {}
ClientLogger = ClientLogger()

def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError

def add_logs_to_response(response):
    response['logs'] = ClientLogger.get_logs()
    ClientLogger.clear_logs()
    return response

@app.route('/generate/melody', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
def generate_melody():
    ClientLogger.log('Generating new melody...')

    content = request.get_json()
    
    length = content['length']
    key = content['key'].replace('#', 's').lower()
    scale = content['scale']
    octaveRange = list(range(content['octaveLowerBound'], content['octaveUpperBound'] + 1))
    disallow_repeats = content['disallowRepeats']

    result = generation_tools.generate_melody(length, key, scale, octaveRange, disallow_repeats)
    
    response = {'generationResult' : result}
    return json.dumps(add_logs_to_response(response))

@app.route('/generate/chords', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
def generate_chords():
    ClientLogger.log('Generating new chord progression...')

    content = request.get_json()
    
    # length = content['length']
    # key = content['key'].replace('#', 's').lower()
    # scale = content['scale']
    # octave_range = list(range(content['octaveLowerBound'], content['octaveUpperBound'] + 1))
    # chord_size_lower_bound = content['chordSizeLowerBound']
    # chord_size_upper_bound = content['chordSizeUpperBound']
    # disallow_repeats = content['disallowRepeats']
    # chance_to_use_chord_leading = content['chanceToUseChordLeadingChart']
    # chance_to_use_voicing_from_library = content['chanceToUseCommonVoicing']
    # v_must_be_dom_7 = content['VMustBeDominant7']
    
    chord_generator = Generator(
        key = content['key'].replace('#', 's').lower(),
        scale = content['scale'],
        length = content['length'],
        chance_to_use_chord_leading=content['chanceToUseChordLeadingChart'], 
        chance_to_use_voicing_from_library = content['chanceToUseCommonVoicing'],
        v_must_be_dom_7 = content['VMustBeDominant7'],
        disallow_repeats = content['disallowRepeats'],
        chord_size_bounds = (content['chordSizeLowerBound'], content['chordSizeUpperBound']),
        octave_range = list(range(content['octaveLowerBound'], content['octaveUpperBound'] + 1)),
    )
    result_chords, result_chord_names = chord_generator.generate_chords()

    DawState['chord_names'] = result_chord_names
    response = {'generationResult' : result_chords}
    return json.dumps(add_logs_to_response(response))

@app.route('/daw-state', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
def update_daw_state():
    content = request.get_json()
    key = content['key'].replace('#', 's')
    scale = content['scale']
    tempo = content['tempo']
    tracks = content['tracks']
    
    DawState['scale'] = scale
    DawState['key'] =  key
    DawState['tempo'] =  tempo
    DawState['tracks'] =  tracks
    chord_names, chord_degrees = name_chords_in_tracks(tracks, key, scale)
    DawState['chord_names'] = chord_names
    DawState['chord_degrees'] = chord_degrees
    
    response = DawState
    return json.dumps(add_logs_to_response(response))

@app.route('/constants', methods=['GET'])
@crossdomain(origin='*')
def get_constants():
    return json.dumps(constants.constants, default=set_default)

@app.route('/midi', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
def create_midi_file():
    content = request.get_json()
    filename, fp = midi_tools.create_midi_file(content)
    return send_file(filename,
        mimetype='audio/midi audio/x-midi',
        as_attachment=True,
        attachment_filename=filename)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404