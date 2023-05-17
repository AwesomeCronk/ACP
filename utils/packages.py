import pathlib, sys

import json5, requests

from constants import paths, platform, _platform


# Sources
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
    elif url[0:8] == 'https://' or url[0:7] == 'http://':
        return 'web'
    # Any other mess that may be put in
    else:
        return 'unknown'

def readSource(url, log):
    urlType = getURLType(url)
    if urlType == 'web':
        try:
            resp = requests.get(url)
        except requests.exceptions.ConnectionError:
            log.error('Unable to connect to remote host ({})'.format(url)); sys.exit(1)
        if resp.ok == False:
            log.error('Request failed, code {} ({})'.format(resp.status_code, url)); sys.exit(1)
        data = resp.content
    
    else:
        try:
            with open(url, 'rb') as file:
                data = file.read()
        except FileNotFoundError:
            log.error('File not found ({})'.format(url)); sys.exit(1)
    
    return data


# Package loading
def loadData(packageName, log):
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

def loadTypedefs(context, log):
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
            },
            'version_separator': ''
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
                log.warning('skipping typedef {}, refuse to override core package_typedef'.format(typedef['name'])); continue
            if typedef['type'] != 'package_typedef':
                log.warning('skipping typedef {}, is not of type package_typedef'.format(typedef['name'])); continue
            
            # Platform compatibility checks
            typedefPlatforms = typedef['releases']['all']['platforms']
            if platform.arch in typedefPlatforms.keys():
                typdedefOSes = typedefPlatforms[platform.arch]
            elif 'any' in typedefPlatforms.keys():
                typdedefOSes = typedefPlatforms['any']
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
                'links': {},
                'version_separator': ''
            }
            for file in typedefInstallData['files']:
                compiledTypedef['files'] = {file['source']: pathlib.Path(file['path']).expanduser().resolve()}
            for link in typedefInstallData['links']:
                compiledTypedef['links'] = {link['source']: pathlib.Path(link['path']).expanduser().resolve()}
            compiledTypedef['version_separator'] = typedefInstallData['version_separator']

            typedefs[typedef['name']] = compiledTypedef

            log.debug('Loaded package typedef: {}'.format(typedef['name']))
    return typedefs


# Installed version detection
def getInstalledVersions(packageData, packageTypedef, log):
    packageName = packageData['name']
    packageFileDir = pathlib.Path(packageTypedef['files']['user'])
    installedVersions = []
    for packageDir in packageFileDir.iterdir():
        if packageName == packageDir.name:
            installedVersions = [versionDir.name for versionDir in packageDir.iterdir()]
            break
    return installedVersions

def getActiveVersion(packageData, packageTypedef, installedVersions, log):
    packageName = packageData['name']
    packageLinkDir = pathlib.Path(packageTypedef['links']['user'])
    activeLink = packageLinkDir.joinpath(packageName).readlink()
    log.debug('activeLink: {}'.format(activeLink.name))
    for version in installedVersions:
        versionTag = ('.' + version).replace('.', packageTypedef['version_separator'])
        if packageName + versionTag == activeLink.name:
            return version
    return None


# Get the requested version if it exists in the package
def getExistingVersion(version, packageData, log):
    if version == 'latest_stable':
        if packageData['latest_stable'] is None:
            log.error('No latest_stable version defined in this package.'); sys.exit(1)
        return packageData['latest_stable']

    elif version == 'latest':
        if packageData['latest'] is None:
            log.error('No latest version defined in this package.'); sys.exit(1)
        return packageData['latest']

    elif version in packageData['releases']:
        return version

    else: log.error('This package has no version "{}".'.format(version)); sys.exit(1)


# Get a compatible platform identifier
def getCompatiblePlatform(packageData, versionToInstall, log):
    platforms = packageData['releases'][versionToInstall]['platforms']
    archs = platforms.keys()
    oses = []
    
    if platform.arch in archs:
        oses = platforms[platform.arch]
        arch = platform.arch
    elif 'any' in archs:
        oses = platforms['any']
        arch = 'any'
    else:
        log.error('No install definition for {}'.format(platform.arch)); sys.exit(1)

    if not platform.os in oses.keys():
        log.error('No install definition for {}'.format(platform.os)); sys.exit(1)

    compatiblePlatform = _platform()
    compatiblePlatform.os = platform.os
    compatiblePlatform.arch = arch

    return compatiblePlatform
