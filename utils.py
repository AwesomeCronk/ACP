import pathlib, shutil, subprocess, shlex, sys, logging

import json5

from constants import paths, platform


# Logging
logStreamHandler = logging.StreamHandler()
logStreamHandler.setLevel(logging.DEBUG)

try: logFileHandler = logging.FileHandler(paths.log, mode='a')
except FileNotFoundError:
    altLogPath = pathlib.Path('./acp_log.txt').resolve()
    logFileHandler = logging.FileHandler(altLogPath, mode='a')
    print('Proper log file not available, writing log to {}'.format(altLogPath))
logFileHandler.setLevel(logging.DEBUG)

logFormatter = logging.Formatter('[%(levelname)s] %(name)s || %(message)s')
logStreamHandler.setFormatter(logFormatter)
logFileHandler.setFormatter(logFormatter)

loadingLogger = logging.getLogger('loading')
loadingLogger.setLevel(logging.DEBUG)
loadingLogger.addHandler(logStreamHandler)
loadingLogger.addHandler(logFileHandler)


# Config
def readConfig(filePath):
    with open(filePath, 'r') as configFile:
        config = json5.load(configFile)
    return config

def writeConfig(filePath, config):
    with open(filePath, 'w') as configFile:
        json5.dump(config, configFile)


# Dependencies
def getDependency(name, logger):
    result = shutil.which(name)
    if result is None:
        logger.error('dependency "{}" not found'.format(name))
        raise RuntimeError('This operation requires that "{}" is installed and available on PATH.'.format(name))
    else:
        return result

def exec(path, command):
    proc = subprocess.Popen([path, *shlex.split(command)], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    return ''.join([line.decode() for line in proc.communicate()]).encode()


# Package URLs
def getURLType(url: str):
    # ./package.acp || /home/user/Downloads/package.acp
    if url[0] in ('.', '/', '~'):    # Going to need changed for Windows support
        return 'file'
    # package
    elif url.count('/') == 0:
        return 'name'
    # repository/package
    elif url.count('/') == 1:
        return 'repo/name'
    # Any other mess that may be put in
    else:
        return 'unknown'


# Package loading
def loadPackageData(packageName):
    log = loadingLogger
    urlType = getURLType(packageName)
    log.debug('URL type: {}'.format(urlType))
    
    if urlType == 'name':
        # Search available repositories for package, then fetch package data
        packageData = ''
        packageFilePath = ''
        raise NotImplementedError

    elif urlType == 'repo/name':
        # Check specified repo for package, then fetch package data
        repo, name = packageName.split('/')

        foundRepository = False
        for repositoryPath in paths.repositories.glob('*'):
            if repo == repositoryPath.name:
                foundRepository = True
                break

        if foundRepository:
            foundPackage = False
            with open(repositoryPath.joinpath('_packages'), 'r') as packageListing:
                for packageEntry in packageListing.readlines():
                    packageName, packagePath = packageEntry.strip().split(': ')
                    if name == packageName:
                        foundPackage = True

            if foundPackage:
                packageFilePath = repositoryPath.joinpath(packagePath)

            else: log.error('Repository "{}" has no entry for package "{}"'.format(repo, name)); sys.exit(1)

        else: log.error('Could not find repository "{}".'.format(repo)); sys.exit(1)

    elif urlType == 'file':
        # Read file to fetch package data
        packageFilePath = pathlib.Path(packageName).expanduser().resolve()

    else:
        log.error('Unable to resolve URL type for "{}"'.format(packageName)); sys.exit(1)

    with open(packageFilePath, 'r') as packageFile:
        packageData = packageFile.read()

    # Parse package data
    return json5.loads(packageData), packageFilePath

def loadPackageTypedefs(context):
    log = loadingLogger
    # Typedefs are handled in this structure during runtime, but stored as a standard .acp package
    typedefs = {
        'package_typedef':
        {
            'files':
            {
                'system': paths.systemData.joinpath('_package_typedefs'),
                'user': paths.userData.joinpath('_package_typedefs')
            },
            'links':    # Shouldn't ever be used, but this way if they are used by accident nothing gets broken
            {
                'system': paths.systemData.joinpath('_package_typedefs/_links'),
                'user': paths.userData.joinpath('_package_typedefs/_links')
            }
        }
    }

    typedefPaths = typedefs['package_typedef']['files'][context].glob('*')

    for typedefPath in typedefPaths:
        log.debug(typedefPath)
        with open(typedefPath, 'r') as typedefFile:
            typedef = json5.load(typedefFile)
            
            # I have finally come to understand that programming is 94% error checking user input and 5% actual logic implementation.
            # I do not know where the other 1% went.
            
            # Name and type checks
            if typedef['name'] == 'package_typedef':
                log.warning('skipping typedef {}, refuse to override core "package_typedef"'.format(typedef['name'])); continue
            if typedef['type'] != 'package_typedef':
                log.warning('skipping typedef {}, is not of type package_typedef'.format(typedef['name'])); continue
            
            # Platform compatibility checks
            typedefPlatforms = typedef['releases']['all']['platforms']
            if platform.arch in typedefPlatforms.keys():
                typdedefOSes = typedefPlatforms[platform.arch]
            elif 'any' in typedefPlatforms.keys():
                typdedefOSes = typedefPlatforms[platform.arch]
            else:
                log.debug('skipping typedef {}, lacks definition for {}'.format(typedef['name'], platform.arch)); continue
            
            if not platform.os in typdedefOSes.keys():
                log.debug('skipping typedef {}, lacks definition for {}'.format(typedef['name'], platform.os)); continue
            typedefInstallData = typdedefOSes[platform.os]

            # System/user definition checks
            if not (
                [file['source'] for file in typedefInstallData['files']]
                == [link['source'] for link in typedefInstallData['links']]
                == ['system', 'user']
            ):
                log.debug('skipping typedef {}, system/user definitions for files and/or links are incorrect'); continue
            
            # Compile the typedef
            compiledTypedef = {
                'files': {},
                'links': {}
            }
            for file in typedefInstallData['files']:
                compiledTypedef['files'] = {file['source']: pathlib.Path(file['path']).expanduser().resolve()}
            for link in typedefInstallData['links']:
                compiledTypedef['links'] = {link['source']: pathlib.Path(link['path']).expanduser().resolve()}

            typedefs[typedef['name']] = compiledTypedef

            log.debug('Loaded package typedef: {}'.format(typedef['name']))
    return typedefs
