import yaml
import json
import os
def loadFromFile(file_name):
    fileContents = ''
    path = '/'.join(os.path.dirname(__file__).split('/')[0:-1])
    with open((os.path.join(path,file_name)), 'r') as file:
        fileContents = file.read()
        file.close()
    return fileContents

def loadConfig(file_name):
    return yaml.load(loadFromFile(file_name))

def loadJsonObject(file_name):
    return json.loads(loadFromFile(file_name))

def writeFile(file_name, content):
    path = '/'.join(os.path.dirname(__file__).split('/')[0:-1])
    with open((os.path.join(path,file_name)), 'w') as file:
        file.write(content)
        file.close()

def writeJsonObject(file_name, object):
    writeFile(file_name, json.dumps(object))

def removeUnnecessaryData(config):
    for printer in config['printers']:
        config['printers'][printer] = {
            'name': config['printers'][printer]['name'],
            'url': config['printers'][printer]['url'],
        }
    return config

def getOfflinePrinterDictionary():
    return {
        'state': 'Printer is unreachable',
        'progress': 0,
        'nozzleTemperature': 0,
        'bedTemperature': 0,
        'fileName': '',
        'timePrinting': 0,
        'timeRemaining': 0,
                }

def getUnreachablePrinterDictionary():
    return {
        'state': 'Octoprint is unreachable',
        'progress': 0,
        'nozzleTemperature': 0,
        'bedTemperature': 0,
        'fileName': '',
        'timePrinting': 0,
        'timeRemaining': 0,
    }

def translatePrinterNamesToPrinterObjects(printerNames, printersConfig):
    printers = {}
    for printerName in printerNames:
        printers[printerName] = printersConfig['printers'][printerName]
    return printers