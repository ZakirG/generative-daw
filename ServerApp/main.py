from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

BASE_URL = os.path.abspath(os.path.dirname(__file__))
CLIENT_APP_FOLDER = os.path.join(BASE_URL, "ClientApp")

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')
    
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404
    


# This is required by zone.js as it need to access the
# "main.js" file in the "ClientApp\app" folder which it
# does by accessing "<your-site-path>/app/main.js"
@app.route('/app/<path:filename>')
def client_app_app_folder(filename):
    return send_from_directory(os.path.join(CLIENT_APP_FOLDER, "app"), filename)

# Custom static data
@app.route('/client-app/<path:filename>')
def client_app_folder(filename):
    return send_from_directory(CLIENT_APP_FOLDER, filename)