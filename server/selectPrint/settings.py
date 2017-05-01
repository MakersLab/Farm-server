import yaml
def load_settings():
    file = open('selectPrint/settings.yml','r')
    settings = yaml.safe_load(file)
    file.close()
    return settings

def load_items_settings():
    file = open(settings['paths']['items'],'r')
    items = yaml.safe_load(file)
    file.close()
    return items

settings = load_settings()
items = load_items_settings()
