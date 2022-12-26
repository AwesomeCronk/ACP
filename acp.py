import argparse, logging, sys
from datetime import datetime

from constants import *
from commands import commands
import utils


def getArgs(argv):
    rootParser = argparse.ArgumentParser(prog='ACP', description='A package manager that aims to eliminate the headaches other package managers are prone to.')
    rootParser.add_argument(
        '-l',
        '--log-level',
        help='importance level cutoff for logging',
        type = str,
        default='config'
    )

    subParsers = rootParser.add_subparsers(dest='command')
    subParsers.required = True
    
    infoParser = subParsers.add_parser('info', help='Fetch info on a package')
    infoParser.set_defaults(function=commands['info'])
    infoParser.add_argument(
        'package',
        help='package for which to fetch info',
        type=str
    )
    infoParser.add_argument(
        '-v',
        '--version',
        help='specific version for which to give info',
        type=str,
        default='<all>'
    )

    add_repoParser = subParsers.add_parser('add-repo', help='Add package repositories')
    add_repoParser.set_defaults(function=commands['add-repo'])
    add_repoParser.add_argument(
        'repository',
        help='repository to add',
        type=str
    )

    update_reposParser = subParsers.add_parser('update-repos', help='Update installed package repositories')
    update_reposParser.set_defaults(function=commands['update-repos'])
    update_reposParser.add_argument(
        '-r',
        '--repository',
        help='repository to update',
        default='<all>',
        type=str
    )

    docsParser = subParsers.add_parser('docs', help='Get documentation for topics relating to ACP')
    docsParser.set_defaults(function=commands['docs'])
    docsParser.add_argument(
        'topic',
        help='topic to search for',
        type=str
    )

    installParser = subParsers.add_parser('install', help='Install a package')
    installParser.set_defaults(function=commands['install'])
    installParser.add_argument(
        'package',
        help='package to install',
        type=str
    )
    installParser.add_argument(
        '-v',
        '--version',
        help='desired version',
        type=str,
        default='latest_stable'
    )
    installParser.add_argument(
        '-s',
        '--system',
        help='install for whole system',
        action='store_true'
    )

    pathsParser = subParsers.add_parser('paths', help='List all paths used by ACP itself')
    pathsParser.set_defaults(function = commands['paths'])

    return rootParser.parse_args(argv)


if __name__ == '__main__':
    # Ensure that Python >= 3.9
    pythonVersion = sys.version_info
    if not (pythonVersion.major == 3 and pythonVersion.minor >= 9):
        print('ACP requires Python 3.9 or higher')
        sys.exit(1)

    args = getArgs(sys.argv[1:])
    log = utils.logging.create('__main__')
    # log.debug('=========={}=========='.format(datetime.now().strftime('%Y-%m-%d %H:%M')))


    # Make sure the environment is set up ok
    if not paths.systemData.exists():
        log.info('Creating system data directory')
        try: paths.systemData.mkdir(parents=True, exist_ok=True)
        except PermissionError: log.info('Unable to create system data directory, must be run as root to do so')

    if not paths.userData.exists():
        log.info('Creating user data directory')
        paths.userData.mkdir(parents=True, exist_ok=True)

    if not paths.systemTypedefs.exists():
        log.info('Creating system typedef directory')
        try: paths.systemTypedefs.mkdir(parents=True, exist_ok=True)
        except PermissionError: log.info('Unable to create system typedef directory, must be run as root to do so')

    if not paths.userTypedefs.exists():
        log.info('Creating user typedef directory')
        paths.userTypedefs.mkdir(parents=True, exist_ok=True)

    if not paths.config.exists():
        log.info('Creating config file')
        paths.config.touch()
        utils.logging.write(paths.config, defaultConfig)

    if not paths.repositories.exists():
        log.info('Creating repository directory')
        paths.repositories.mkdir(parents=True, exist_ok=True)


    config = utils.config.read(paths.config)

    if args.log_level == 'config':
        if config['log-level'] in logLevels.keys():
            utils.logging.streamHandler.setLevel(logLevels[config['log-level']])
        else: log.error('Invalid log level "{}" in config'.format(config['log-level'])); sys.exit(1)

    else:
        if args.log_level in logLevels.keys():
            utils.logging.streamHandler.setLevel(logLevels[args.log_level])
        else: log.error('Invalid log level "{}"'.format(args.log_level)); sys.exit(1)

    args.function(args, config)
