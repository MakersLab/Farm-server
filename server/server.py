from flask import Flask, send_from_directory
from lib.utils import loadConfig, removeUnnecessaryData
import json
from flask_cors import CORS, cross_origin
import api
import selectPrint
import traceback

CONFIG = loadConfig('config.yml')
FILE_UPLOAD_PATH = CONFIG['api']['file-upload-path']

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = FILE_UPLOAD_PATH

@app.route('/api/printer-config')
def printerConfig():
    return json.dumps(removeUnnecessaryData(loadConfig('printers.yml')))

@app.route('/api/test')
def test():
    return 'test of fetch'

@app.route('/<string:path>')
def files(path):
    print(path)
    return send_from_directory('static',path)

@app.route('/')
def index():
    return send_from_directory('static','index.html')

api.add_blueprint(app)
selectPrint.add_blueprint(app)

if __name__ == '__main__':
    app.run(debug=True, port=CONFIG['api']['port'],host='0.0.0.0',threaded=True)
