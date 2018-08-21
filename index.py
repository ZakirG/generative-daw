from flask import Flask, render_template
app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')
    
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404