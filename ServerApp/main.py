from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
import os
import json
import random
from crossdomain import crossdomain

app = Flask(__name__)
CORS(app)

BASE_URL = os.path.abspath(os.path.dirname(__file__))
CLIENT_APP_FOLDER = os.path.join(BASE_URL, "ClientApp")

possible_notes = [
    {'note' : 'b', 'octave' : 2},
    {'note' : 'as', 'octave' : 2},
    {'note' : 'a', 'octave' : 2},
    {'note' : 'gs', 'octave' : 2},
    {'note' : 'g', 'octave' : 2},
    {'note' : 'fs', 'octave' : 2},
    {'note' : 'f', 'octave' : 2},
    {'note' : 'e', 'octave' : 2},
    {'note' : 'ds', 'octave' : 2},
    {'note' : 'd', 'octave' : 2},
    {'note' : 'cs', 'octave' : 2},
    {'note' : 'c', 'octave' : 2},
    {'note' : 'b', 'octave' : 1},
    {'note' : 'as', 'octave' : 1},
    {'note' : 'a', 'octave' : 1},
    {'note' : 'gs', 'octave' : 1},
    {'note' : 'g', 'octave' : 1},
    {'note' : 'fs', 'octave' : 1},
    {'note' : 'f', 'octave' : 1},
    {'note' : 'e', 'octave' : 1},
    {'note' : 'ds', 'octave' : 1},
    {'note' : 'd', 'octave' : 1},
    {'note' : 'cs', 'octave' : 1},
    {'note' : 'c', 'octave' : 1}]

allowed_chord_sizes = range(3, 7)

@app.route('/generate/melody/<string:generation_type>/<int:length>', methods=['GET'])
@crossdomain(origin='*')
def generate_melody(generation_type, length):
    print(generation_type + ' ' + str(length))
    result = None
    if generation_type == 'random':    
        result = generate_random_melody(length)
    
    response = {'generationResult' : result}
    return json.dumps(response);

@app.route('/generate/chords/<string:generation_type>/<int:length>', methods=['GET'])
@crossdomain(origin='*')
def generate_chords(generation_type, length):
    print(generation_type + ' ' + str(length))
    result = None
    if generation_type == 'random':    
        result = generate_random_chords(length)
    
    response = {'generationResult' : result}
    return json.dumps(response);


def generate_random_melody(length):
    result = []
    for i in range(length):
        result.append([random.choice(possible_notes)])
    
    print('melody:' + str(result))
    return result
    
def generate_random_chords(length):
    result = []
    
    for i in range(length):
        num_notes_in_chord = random.choice(allowed_chord_sizes)
        chord = []
        for j in range(num_notes_in_chord):
            chord.append(random.choice(possible_notes))
        result.append(chord)
            
    print('chords:' + str(result))
    return result
    
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404
