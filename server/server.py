from flask import Flask
from lib.utils import loadConfig, removeUnnecessaryData
import json
from flask_cors import CORS, cross_origin

CONFIG = loadConfig('config.yml')

app = Flask(__name__)
CORS(app)

@app.route('/api/printer-config')
def printerConfig():
    return json.dumps(removeUnnecessaryData(loadConfig('printers.yml')))

if __name__ == '__main__':
    app.run(debug=True, port=CONFIG['api']['port'],host='0.0.0.0')