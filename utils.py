import argparse, pathlib, shutil, subprocess, shlex, sys, logging

import json5

from constants import paths, platform


logStreamHandler = logging.StreamHandler()
logStreamHandler.setLevel(logging.DEBUG)

logFileHandler = logging.FileHandler(paths.log, mode='a')
logFileHandler.setLevel(logging.DEBUG)

logFormatter = logging.Formatter('%(levelname)8s | %(name)s - %(message)s')
logStreamHandler.setFormatter(logFormatter)
logFileHandler.setFormatter(logFormatter)

loadingLogger = logging.getLogger('loading')
loadingLogger.setLevel(logging.DEBUG)


def readConfig(filePath):
    with open(filePath, 'r') as configFile:
        config = json5.load(configFile)
    return config

def writeConfig(filePath, config):
    with open(filePath, 'w') as configFile:
        json5.dump(config, configFile)


def getDependency(name, logger):
    result = shutil.which(name)
    if result is None:
        logger.error('dependency "{}" not found'.format(name))
        raise RuntimeError('This operation requires that "{}" is installed and available on PATH.'.format(name))
    else:
        return result


def getURLType(url: str):
    # ./package.acp | /home/user/Downloads/package.acp
    if url[0] in ('.', '/'):    # Going to need changed for Windows support
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

def loadPackageData(packageName):
    log = loadingLogger
    urlType = getURLType(packageName)
    log.debug('URL type: {}'.format(urlType))
    
    if urlType == 'name':
        # Search available repositories for package, then fetch package data
        packageData = ''

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
                with open(repositoryPath.joinpath(packagePath), 'r') as packageFile:
                    packageData = packageFile.read()

            else: log.error('Repository "{}" has no entry for package "{}"'.format(repo, name)); sys.exit(1)

        else: log.error('Could not find repository "{}".'.format(repo)); sys.exit(1)

    elif urlType == 'file':
        # Read file to fetch package data
        with open(pathlib.Path(packageName).resolve(), 'r') as file:
            packageData = file.read()

    else:
        log.error('Unable to resolve URL type for "{}"'.format(packageName)); sys.exit(1)

    # Parse package data
    return json5.loads(packageData)

def loadPackageTypes():
    log = loadingLogger
    typeDefs = {
        'package_typedef':
        {
            'global':
            {
                'install_path': paths.globalData.joinpath('_packageTypes'),
                'link_path': paths.globalData.joinpath('_packageTypes/links')   # Shouldn't ever be used, but this way if it used is by accident nothing gets broken
            },
            'local':
            {
                'install_path': paths.localData.joinpath('_packageTypes'),
                'link_path': paths.localData.joinpath('_packageTypes/links')    # Shouldn't ever be used, but this way if it used is by accident nothing gets broken
            }
        }
    }

    log.debug(typeDefs['package_typedef']['local']['install_path'])
    log.debug(typeDefs['package_typedef']['local']['install_path'].glob('*'))
    typeDefPaths = typeDefs['package_typedef']['local']['install_path'].glob('*')
    for typeDefPath in typeDefPaths:
        log.debug(typeDefPath)
        with open(typeDefPath, 'r') as typeDefFile:
            typeDef = json5.load(typeDefFile)
            
            # I have finally come to understand that programming is 94% error checking user input and 5% actual logic implementation.
            # I do not know where the other 1% went.
            if typeDef['name'] == 'package_typedef':
                log.debug('Not loading "{}" ({}), refuse to override core "package_typedef".'.format(typeDef['name'], typeDefPath))
                continue
            if typeDef['type'] != 'package_typedef':
                log.debug('Not loading "{}" ({}), not of type "package_typedef".'.format(typeDef['name'], typeDefPath))
                continue
            if list(typeDef['versions'].keys()) != ['global', 'local']:
                log.debug('Not loading "{}" ({}), lacks global and/or local definitions.'.format(typeDef['name'], typeDefPath))
                continue
            if (not platform in typeDef['global']['platforms'].keys()) or (not platform in typeDef['local']['platforms'].keys()):
                log.debug('Not loading "{}" ({}), Lacks definition for {}.'.format(typeDef['name'], typeDefPath, platform))
                continue

            files = typeDef['global']['platforms'][platform]['files']
            for file in files:
                if file['source'] == 'packages':
                    globalPackages = file['path']
                if file['source'] == 'links':
                    globalLinks = file['path']
            files = typeDef['local']['platforms'][platform]['files']
            for file in files:
                if file['source'] == 'packages':
                    localPackages = file['path']
                if file['source'] == 'links':
                    localLinks = file['path']

            typeDefs[typeDef['name']] = {
                'global':
                {
                    'install_path': globalPackages,
                    'link_path': globalLinks
                },
                'local':
                {
                    'install_path': localPackages,
                    'link_path': localLinks
                }
            }
            log.debug('Loaded package typedef "{}".'.format(typeDef['name']))

    return typeDefs


def exec(path, command):  # Wrapper for subprocess to facilitate one-line git 
    proc = subprocess.Popen([path, *shlex.split(command)], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    return ''.join([line.decode() for line in proc.communicate()]).encode()
