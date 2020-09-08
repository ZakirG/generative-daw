from flask import Flask, render_template, send_from_directory
from flask import request, send_file
from flask_cors import CORS
import os
import json
from crossdomain import crossdomain
import constants
import generation_tools
import midi_tools

app = Flask(__name__)
CORS(app)

BASE_URL = os.path.abspath(os.path.dirname(__file__))
CLIENT_APP_FOLDER = os.path.join(BASE_URL, "ClientApp")

DawState = {}

def set_default(obj):
    if isinstance(obj, set):
        return list(obj)
    raise TypeError

@app.route('/generate/melody/<string:key>/<string:scale>/<string:octave_constraint>/<string:generation_type>/<int:length>', methods=['GET'])
@crossdomain(origin='*')
def generate_melody(key, scale, octave_constraint, generation_type, length):
    result = None
    if generation_type == 'random':
        result = generation_tools.generate_random_melody(length, key, scale, octave_constraint)
    
    response = {'generationResult' : result}
    return json.dumps(response);

@app.route('/generate/chords/<string:key>/<string:scale>/<string:octave_constraint>/<string:generation_type>/<int:length>', methods=['GET'])
@crossdomain(origin='*')
def generate_chords(key, scale, octave_constraint, generation_type, length):
    result = None
    if generation_type == 'random':    
        result = generation_tools.generate_random_chords(length, key, scale, octave_constraint)
    
    response = {'generationResult' : result}
    return json.dumps(response);

@app.route('/daw-state', methods=['POST', 'OPTIONS'])
@crossdomain(origin='*')
def update_daw_state():
    content = request.get_json()
    
    DawState['scale'] =  content['scale']
    DawState['key'] =  content['key']
    DawState['tempo'] =  content['tempo']
    DawState['tracks'] =  content['tracks']
    DawState['chord_names'] = generation_tools.name_chords_in_tracks(content['tracks'])
    # print(DawState)
    response = DawState
    return json.dumps(response)

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