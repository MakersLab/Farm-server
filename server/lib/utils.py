import yaml

def loadFromFile(file_name):
    fileContents = ''
    with open(file_name, 'r') as file:
        fileContents = file.read()
    return fileContents

def loadConfig(file_name):
    return yaml.load(loadFromFile(file_name))