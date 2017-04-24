from flask import Blueprint, request
from werkzeug.utils import secure_filename
import os
import inspect

def getSelectedPrinters():
    return request.form['selectedPrinters']

def add_blueprint(app=None):
    api = Blueprint('Printer API',__name__, url_prefix='/api')

    @api.route('/pause', methods=['POST'])
    def pause():
        print(getSelectedPrinters())
        return 'pause'

    @api.route('/resume', methods=['POST'])
    def resume():
        print(getSelectedPrinters())
        return 'resume'

    @api.route('/print', methods=['POST'])
    def printer():
        print(request.form['selectedPrinters'])
        return 'print'

    @api.route('/load', methods=['POST'])
    def load():
        print('processing')
        file = request.files['file']
        print('not anymore')
        filename = secure_filename(file.filename)
        file.save(os.path.join('upload',filename))
        return filename

    app.register_blueprint(api)