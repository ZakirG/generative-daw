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

possible_octaves = range(1,3)

chromatic_scale =  [
    {'note' : 'b'},
    {'note' : 'as'},
    {'note' : 'a'},
    {'note' : 'gs'},
    {'note' : 'g'},
    {'note' : 'fs'},
    {'note' : 'f'},
    {'note' : 'e'},
    {'note' : 'ds'},
    {'note' : 'd'},
    {'note' : 'cs'},
    {'note' : 'c'} ]

possible_notes = []
for octave in possible_octaves:
    for note in chromatic_scale:
        possible_notes.append({'note' : note['note'], 'octave' : octave})

allowed_chord_sizes = range(3, 7)

scales = {
            'maj' : {'name' : 'major', 'intervals' : [2,2,1,2,2,2,1 ] },
            'min' : {'name' : 'minor', 'intervals' : [2,1,1,2,2,1,2 ] },
            'dhmaj' : {'name' : 'maj (b2 b6)', 'intervals' : [1,3,1,2,1,3,1 ] },
        }

@app.route('/generate/melody/<string:key>/<string:scale>/<string:generation_type>/<int:length>', methods=['GET'])
@crossdomain(origin='*')
def generate_melody(key, scale, generation_type, length):
    print(generation_type + ' ' + str(length))
    print('key: ' + key + ' scale: ' + scale)
    result = None
    if generation_type == 'random':
        result = generate_random_melody(length, key, scale)
    
    response = {'generationResult' : result}
    return json.dumps(response);

@app.route('/generate/chords/<string:key>/<string:scale>/<string:generation_type>/<int:length>', methods=['GET'])
@crossdomain(origin='*')
def generate_chords(key, scale, generation_type, length):
    print(generation_type + ' ' + str(length))
    print('key: ' + key + ' scale: ' + scale)
    result = None
    if generation_type == 'random':    
        result = generate_random_chords(length, key, scale)
    
    response = {'generationResult' : result}
    return json.dumps(response);

def get_key_scale_notes(key, scale_code):
    possible_notes_in_asc_order = list(reversed(possible_notes))
    index_of_key = possible_notes_in_asc_order.index({'note' : key.lower(), 'octave' : 1})
    notes_sorted_starting_at_root = possible_notes_in_asc_order[index_of_key:] + possible_notes_in_asc_order[:index_of_key]
    intervals = scales[scale_code]['intervals']
    key_scale_notes = []
    i = 0
    for interval in intervals:
        unique_scale_note = notes_sorted_starting_at_root[i + interval]
        for octave in possible_octaves:
            key_scale_notes.append({ 'note' : unique_scale_note['note'], 'octave' : octave })
        i = i + interval
    return key_scale_notes

def generate_random_melody(length, key, scale):
    key_scale_possible_notes = possible_notes
    if key != 'any':
        key_scale_possible_notes = get_key_scale_notes(key, scale)
    
    result = []
    for i in range(length):
        result.append([random.choice(key_scale_possible_notes)])
    
    print('melody:' + str(result))
    return result
    
def generate_random_chords(length, key, scale):
    key_scale_possible_notes = possible_notes
    if key != 'any':
        key_scale_possible_notes = get_key_scale_notes(key, scale)
    
    result = []
    for i in range(length):
        num_notes_in_chord = random.choice(allowed_chord_sizes)
        chord = []
        for j in range(num_notes_in_chord):
            chord.append(random.choice(key_scale_possible_notes))
        result.append(chord)
            
    print('chords:' + str(result))
    return result
    
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404
