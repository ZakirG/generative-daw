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
    {'color' : 'white', 'note' : 'b', 'octave' : 2},
    {'color' : 'black', 'note' : 'as', 'octave' : 2},
    {'color' : 'white', 'note' : 'a', 'octave' : 2},
    {'color' : 'black', 'note' : 'gs', 'octave' : 2},
    {'color' : 'white', 'note' : 'g', 'octave' : 2},
    {'color' : 'black', 'note' : 'fs', 'octave' : 2},
    {'color' : 'white', 'note' : 'f', 'octave' : 2},
    {'color' : 'white', 'note' : 'e', 'octave' : 2},
    {'color' : 'black', 'note' : 'ds', 'octave' : 2},
    {'color' : 'white', 'note' : 'd', 'octave' : 2},
    {'color' : 'black', 'note' : 'cs', 'octave' : 2},
    {'color' : 'white', 'note' : 'c', 'octave' : 2},
    {'color' : 'white', 'note' : 'b', 'octave' : 1},
    {'color' : 'black', 'note' : 'as', 'octave' : 1},
    {'color' : 'white', 'note' : 'a', 'octave' : 1},
    {'color' : 'black', 'note' : 'gs', 'octave' : 1},
    {'color' : 'white', 'note' : 'g', 'octave' : 1},
    {'color' : 'black', 'note' : 'fs', 'octave' : 1},
    {'color' : 'white', 'note' : 'f', 'octave' : 1},
    {'color' : 'white', 'note' : 'e', 'octave' : 1},
    {'color' : 'black', 'note' : 'ds', 'octave' : 1},
    {'color' : 'white', 'note' : 'd', 'octave' : 1},
    {'color' : 'black', 'note' : 'cs', 'octave' : 1},
    {'color' : 'white', 'note' : 'c', 'octave' : 1}]

@app.route('/generate/melody/<string:generation_type>/<int:length>', methods=['GET'])
@crossdomain(origin='*')
def generate_melody(generation_type, length):
    print(generation_type + ' ' + str(length))
    result = None
    if generation_type == 'random':    
        result = generate_random_melody(length)
    
    response = {'generationResult' : result}
    return json.dumps(response);

def generate_random_melody(length):
    result = []
    for i in range(length):
        result.append(random.choice(possible_notes))
    return result
    
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404
