import logging, os, shutil

from constants import logNameLen
from utils import *


def command_info(args, config):
    log = logging.getLogger('info'.ljust(logNameLen))
    log.setLevel(logging.DEBUG)
    log.addHandler(logStreamHandler)
    log.addHandler(logFileHandler)

    data = loadPackageData(args.package)
    output = '\n'.join([
        'Information for {}:'.format(data['name']),
        'Type: {}'.format(data['type']),
        'Latest release: {}'.format(data['latest']),
        'Latest stable release: {}'.format(data['latest_stable']),
        'Releases:'
    ])

    # It's messy but it works. Don't look too close.
    for release in data['releases'].keys():
        if args.version == release or args.version == '<all>':
            output += '\n* {}'.format(release)
            output += '\n  * Release notes: {}'.format(data['releases'][release]['release_notes'])
            output += '\n  * Stable: {}'.format('yes' if data['releases'][release]['stable'] else 'no')
            output += '\n  * Platforms:'
            for platform in data['releases'][release]['platforms'].keys():
                output += '\n    * {} ({})'.format(platform, ', '.join([os for os in data['releases'][release]['platforms'][platform].keys()]))

    print(output)

def command_docs(args, config):
    log = logging.getLogger('docs'.ljust(logNameLen))
    log.setLevel(logging.DEBUG)
    log.addHandler(logStreamHandler)
    log.addHandler(logFileHandler)
    log.debug('Fetching docs for {}...'.format(args.topic))
    print('Listing documentation for {}:'.format(args.topic))
