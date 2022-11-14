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
    # Data paths
    paths.systemData = pathlib.Path('/etc/acp')
    paths.userData = pathlib.Path('~/.local/share/acp').expanduser()
    paths.temp = pathlib.Path('/tmp/acp')
    
    # Configuration and runtime stuff
    paths.log = paths.userData.joinpath('log.txt')
    paths.config = paths.userData.joinpath('config.json')
    
    # Repository and typedef storage
    paths.repositories = paths.userData.joinpath('repositories')
    paths.systemTypedefs = paths.systemData.joinpath('_package_typedefs')
    paths.userTypedefs = paths.userData.joinpath('_package_typedefs')

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

logNameLen = 8

defaultConfig = {
    'log-level': 'info'
}
