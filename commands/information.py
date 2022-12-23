import logging

from constants import logNameLen
from utils import *


def command_info(args, config):
    log = logging.getLogger('info'.ljust(logNameLen))
    log.setLevel(logging.DEBUG)
    log.addHandler(logStreamHandler)
    log.addHandler(logFileHandler)

    packageData, packageFilePath = loadPackageData(args.package)
    packageTypedefs = loadPackageTypedefs('system')
    packageTypedefs.update(loadPackageTypedefs('user'))
    installedVersions = getInstalledVersions(packageData, packageTypedefs[packageData['type']], log)
    activeVersion = getActiveVersion(packageData, packageTypedefs[packageData['type']], installedVersions, log)

    output = '\n'.join([
        'Information for {}:'.format(packageData['name']),
        'Type: {}'.format(packageData['type']),
        'Latest release: {}'.format(packageData['latest']),
        'Latest stable release: {}'.format(packageData['latest_stable']),
        'Active version: {}'.format(activeVersion),
        'Releases:'
    ])

    # It's messy but it works. Don't look too close.
    for release in packageData['releases'].keys():
        if args.version == release or args.version == '<all>':
            output += '\n* {}{}{}'.format(
                release,
                ' (stable)' if packageData['releases'][release]['stable'] else '',
                ' (installed)' if release in installedVersions else ''
            )
            output += '\n  Release notes: {}'.format(packageData['releases'][release]['release_notes'])
            output += '\n  Platforms:'
            for platform in packageData['releases'][release]['platforms'].keys():
                output += '\n  * {} ({})'.format(platform, ', '.join([os for os in packageData['releases'][release]['platforms'][platform].keys()]))

    print(output)

def command_docs(args, config):
    log = logging.getLogger('docs'.ljust(logNameLen))
    log.setLevel(logging.DEBUG)
    log.addHandler(logStreamHandler)
    log.addHandler(logFileHandler)
    log.debug('Fetching docs for {}...'.format(args.topic))
    print('Listing documentation for {}:'.format(args.topic))

def command_paths(args, config):
    log = logging.getLogger('paths'.ljust(logNameLen))
    log.setLevel(logging.DEBUG)
    log.addHandler(logStreamHandler)
    log.addHandler(logFileHandler)
    for path in dir(paths):
        if path[0:2] != '__' and path != 'forbiddenCharacters':
            print('{}: {}'.format(path, getattr(paths, path)))
