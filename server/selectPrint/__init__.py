from flask import Blueprint, request, render_template, send_from_directory
import jinja2
import selectPrint.settings

template_dir = 'selectPrint/templates'
loader = jinja2.FileSystemLoader(template_dir)
environment = jinja2.Environment(loader=loader)

def add_blueprint(app=None):
    selectPrint = Blueprint('Select-Print', __name__, url_prefix='/select-print')
    selectPrint.jinja_loader = loader

    @selectPrint.route('')
    def index():
        return render_template('index.jinja2', items=settings.items)

    @selectPrint.route('/select-print/static/<path:filename>')
    def static(filename):
        return send_from_directory('selectPrint/static', filename)

    app.register_blueprint(selectPrint)