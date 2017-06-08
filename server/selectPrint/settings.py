import yaml
import os

def load_settings():
    path = '/'.join(os.path.dirname(__file__).split('/'))
    file = open(os.path.join(path,'settings.yml'),'r')
    settings = yaml.safe_load(file)
    file.close()
    return settings

def load_items_settings():
    path = '/'.join(os.path.dirname(__file__).split('/'))
    file = open(os.path.join(path,settings['paths']['items']),'r')
    items = yaml.safe_load(file)
    file.close()
    return items

settings = load_settings()
items = load_items_settings()
