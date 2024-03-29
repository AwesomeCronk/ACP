import logging, pathlib

import simpleANSI as ansi
from simpleANSI.graphics import setGraphicsMode

from constants import paths


streamHandler = logging.StreamHandler()
streamHandler.setLevel(logging.DEBUG)

try: fileHandler = logging.FileHandler(paths.log, mode='a')
except FileNotFoundError:
    altLogPath = pathlib.Path('./acp_log.txt').resolve()
    logFileHandler = logging.FileHandler(altLogPath, mode='a')
    print('Proper log file not available, writing log to {}'.format(altLogPath))
fileHandler.setLevel(logging.DEBUG)

class _colorFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        logging.Formatter.__init__(self, *args, **kwargs)

    def format(self, record):
        baseStr = logging.Formatter.format(self, record)
        colors = {
            'DEBUG': setGraphicsMode(ansi.graphics.fgBlue),
            'INFO': setGraphicsMode(ansi.graphics.normal),
            'WARNING': setGraphicsMode(ansi.graphics.fgYellow),
            'ERROR': setGraphicsMode(ansi.graphics.fgRed),
            'CRITICAL': setGraphicsMode(ansi.graphics.fgMagenta)
        }
        for level in colors.keys():
            if level in baseStr:
                return colors[level] + baseStr + colors['INFO']
        return baseStr
        
format = '%(name)s:%(levelname)s: %(message)s'
basicFormatter = logging.Formatter(format)
colorFormatter = _colorFormatter(format)
streamHandler.setFormatter(colorFormatter)
fileHandler.setFormatter(basicFormatter)


def create(name):
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    log.addHandler(streamHandler)
    log.addHandler(fileHandler)
    return log
