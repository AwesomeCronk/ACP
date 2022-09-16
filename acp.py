import logging, sys
from datetime import datetime

from constants import *
from utils import *
from commands import *


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
    infoParser.set_defaults(function=info)
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
    add_repoParser.set_defaults(function=add_repo)
    add_repoParser.add_argument(
        'repository',
        help='repository to add',
        type=str
    )

    update_reposParser = subParsers.add_parser('update-repos', help='Update installed package repositories')
    update_reposParser.set_defaults(function=update_repos)
    update_reposParser.add_argument(
        '-r',
        '--repository',
        help='repository to update',
        default='<all>',
        type=str
    )

    docsParser = subParsers.add_parser('docs', help='Get documentation for topics relating to ACP')
    docsParser.set_defaults(function=docs)
    docsParser.add_argument(
        'topic',
        help='topic to search for',
        type=str
    )

    installParser = subParsers.add_parser('install', help='Install a package')
    installParser.set_defaults(function=install)
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

    return rootParser.parse_args(argv)


if __name__ == '__main__':
    args = getArgs(sys.argv[1:])
    log = logging.getLogger('__main__')
    log.setLevel(logging.DEBUG)
    log.addHandler(logStreamHandler)
    log.addHandler(logFileHandler)
    log.debug('=========={}=========='.format(datetime.now().strftime('%Y-%m-%d %H:%M')))


    # Make sure the environment is set up ok
    if not paths.userData.exists():
        log.info('User data directory not found, creating it now')
        paths.userData.mkdir(parents=True, exist_ok=True)

    if not paths.systemData.exists():
        log.info('System data directory not found, creating it now')
        try: paths.systemData.mkdir(parents=True, exist_ok=True)
        except PermissionError: log.info('Unable to create system data directory, must be run as root to do so')

    if not paths.config.exists():
        log.info('Config file not found, creating it now')
        paths.config.touch()
        writeConfig(paths.config, defaultConfig)

    if not paths.repositories.exists():
        log.info('Repository directory not found, creating it now')
        paths.repositories.mkdir(parents=True, exist_ok=True)


    config = readConfig(paths.config)

    if args.log_level == 'config':
        if config['log-level'] in logLevels.keys():
            logStreamHandler.setLevel(logLevels[config['log-level']])
        else: log.error('Invalid log level "{}" from configuration'.format(config['log-level'])); sys.exit(1)

    else:
        if args.log_level in logLevels.keys():
            logStreamHandler.setLevel(logLevels[args.log_level])
        else: log.error('Invalid log level "{}"'.format(args.log_level)); sys.exit(1)

    args.function(args, config)
