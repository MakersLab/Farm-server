from flask import Blueprint, request
from werkzeug.utils import secure_filename
import os
import inspect
from lib.utils import loadConfig, translatePrinterNamesToPrinterObjects
from lib.requests import makeRequest

COMMAND_PRINT = 'COMMAND_PRINT'
COMMAND_PAUSE = 'COMMAND_PAUSE'
COMMAND_RESUME = 'COMMAND_RESUME'

PRINTERS_CONFIG_PATH = 'printers.yml'

def getSelectedPrinters():
    return request.form['selectedPrinters'].split(',')

def add_blueprint(app=None):
    api = Blueprint('Printer API',__name__, url_prefix='/api')

    @api.route('/pause', methods=['POST'])
    def pause():
        makeRequest(COMMAND_PAUSE,translatePrinterNamesToPrinterObjects(getSelectedPrinters(), loadConfig(PRINTERS_CONFIG_PATH)))

        return 'pause'

    @api.route('/resume', methods=['POST'])
    def resume():
        print(getSelectedPrinters())
        makeRequest(COMMAND_RESUME,translatePrinterNamesToPrinterObjects(getSelectedPrinters(), loadConfig(PRINTERS_CONFIG_PATH)))

        return 'resume'

    @api.route('/print', methods=['POST'])
    def printer():
        makeRequest(COMMAND_PRINT,translatePrinterNamesToPrinterObjects(getSelectedPrinters(), loadConfig(PRINTERS_CONFIG_PATH)))

        return 'print'

    @api.route('/load', methods=['POST'])
    def load():
        file = request.files['file']
        filename = secure_filename(file.filename)
        file.save(os.path.join('upload',filename))
        return filename

    app.register_blueprint(api)