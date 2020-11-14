from flask import Flask, render_template, send_from_directory
from flask import request, send_file
from flask_cors import CORS
import os
import json
from crossdomain import crossdomain
import constants
from music_theory import name_chords_in_tracks
import midi_tools
from client_logging import ClientLogger
from chords_generator import ChordsGenerator
from melody_generator import MelodyGenerator
app = Flask(__name__)
CORS(app)

BASE_URL = os.path.abspath(os.path.dirname(__file__))
CLIENT_APP_FOLDER = os.path.join(BASE_URL, "ClientApp")

DawState = {'chord_names': [[]], 'chord_degrees': [[]]}
ClientLogger = ClientLogger()
# Maps hashed chord sets to names. One dict for each track

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
    mel_generator = MelodyGenerator(content)
    result = mel_generator.generate_melody()
    
    response = {'generation_result' : result}
    return json.dumps(add_logs_to_response(response))

@app.route('/generate/chords', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
def generate_chords():
    content = request.get_json()
    chord_generator = ChordsGenerator(content)
    result_chords, result_chord_names = chord_generator.generate_chords()

    DawState['chord_names'][content['trackNumber']] = result_chord_names
    response = {'generation_result' : result_chords, 'chord_names': result_chord_names}
    return json.dumps(add_logs_to_response(response))

@app.route('/daw-state', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
def update_daw_state():
    content = request.get_json()
    key = content['key'].replace('#', 's')
    scale = content['scale']
    tempo = content['tempo']
    tracks = content['tracks']
    sequences = content['sequences']
    
    DawState['scale'] = scale
    DawState['key'] =  key
    DawState['tempo'] =  tempo
    DawState['tracks'] =  tracks

    chord_names, chord_degrees = name_chords_in_tracks(sequences, key, scale)
    DawState['chord_names'] = chord_names
    DawState['chord_degrees'] = chord_degrees
    DawState['sequences'] = sequences
    
    response = DawState
    return json.dumps(add_logs_to_response(response))

@app.route('/constants', methods=['GET'])
@crossdomain(origin='*')
def get_constants():
    return json.dumps(constants.constants, default=set_default)

@app.route('/sequence-to-midi', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
def sequence_to_midi_file():
    content = request.get_json()
    filename, fp = midi_tools.create_midi_file(content)
    return send_file(filename,
        mimetype='audio/midi audio/x-midi',
        as_attachment=True,
        attachment_filename=filename)
    
@app.route('/midi-to-sequence', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
def midi_file_to_sequence():
    content = request.get_json()
    midi_speed_change = float(request.form['midiSpeedChange'])

    sequence, tempo = midi_tools.midi_file_to_sequence(request.files['file'], midi_speed_change)
    return json.dumps({ 'sequence': sequence, 'tempo': tempo}, default=set_default)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404