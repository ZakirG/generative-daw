from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
import os
import json

app = Flask(__name__)
CORS(app)

BASE_URL = os.path.abspath(os.path.dirname(__file__))
CLIENT_APP_FOLDER = os.path.join(BASE_URL, "ClientApp")

@app.route('/generate/melody', methods=['GET'])
def generate_melody():
    print('inside generate_melody()')
    response = {'generationResult' : [2,2]}
    return json.dumps(response);
    
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404