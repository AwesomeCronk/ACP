import logging, pathlib
import platform as plt


# Platform
class _platform: pass
platform = _platform()
platform.os = plt.uname().system
platform.arch = plt.uname().machine


# File paths
class _paths: pass
paths = _paths()

if platform.os == 'Linux':
    paths.globalData = pathlib.Path('/etc/ACP')
    paths.localData = pathlib.Path('~/.local/share/ACP').expanduser()
    paths.log = paths.localData.joinpath('log.txt')
    paths.config = paths.localData.joinpath('config.json')
    paths.repositories = paths.localData.joinpath('repositories')
elif platform.os == 'Windows':
    raise RuntimeError('Windows is not yet supported - I hope to change that soon!')
else:
    raise RuntimeError('Platform "{}" is unrecognized and unsupported.'.format(platform))

paths.forbiddenCharacters = '<>:"/\\|?*' + ''.join([int.to_bytes(i, 1, 'big').decode('ascii') for i in range(32)])


# URLs
class _urls: pass
urls = _urls()
urls.docsRoot ='https://raw.githubusercontent.com/AwesomeCronk/ACP/master/docs/'   # Base url to fetch documentation


# Errors
class ConfigError(Exception): pass


# Miscellaneous
logLevels = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

defaultConfig = {
    'debug-level': 'info'
}