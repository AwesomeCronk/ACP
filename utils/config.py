import json5


def read(filePath):
    with open(filePath, 'r') as configFile:
        config = json5.load(configFile)
    return config

def write(filePath, config):
    with open(filePath, 'w') as configFile:
        json5.dump(config, configFile)
