import yaml
import json

def loadFromFile(file_name):
    fileContents = ''
    with open(file_name, 'r') as file:
        fileContents = file.read()
        file.close()
    return fileContents

def loadConfig(file_name):
    return yaml.load(loadFromFile(file_name))

def loadJsonObject(file_name):
    return json.loads(loadFromFile(file_name))

def removeUnnecessaryData(config):
    for printer in config['printers']:
        config['printers'][printer] = {
            'name': config['printers'][printer]['name'],
            'url': config['printers'][printer]['url'],
        }
    return config

def getOfflinePrinterDictionary():
    return {
        'state': 'Not working',
        'progress': 0,
        'nozzleTemperature': 0,
        'bedTemperature': 0,
        'fileName': 'x',
        'timePrinting': 0,
        'timeRemaining': 0,
                }