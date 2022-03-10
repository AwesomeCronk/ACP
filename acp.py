import argparse, json, pathlib, logging, sys


### Constants ###
platform = sys.platform

# File paths
if platform == 'linux':
    dataDirPath = pathlib.Path('~/.local/share/ACP').expanduser()
    logPath = dataDirPath.joinpath('log.txt')
    configPath = dataDirPath.joinpath('config.json')
elif platform == 'win32':
    raise RuntimeError('Windows is not yet supported - I hope to change that soon!')
else:
    raise RuntimeError('Platform "{}" is not recognized and therefore not supported.'.format(platform))

# URLs
docsRootURL='https://raw.githubusercontent.com/AwesomeCronk/ACP/master/docs/'   # Base url to fetch documentation

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

### Utils ###
def getArgs(argv):
    rootParser = argparse.ArgumentParser(prog='ACP', description='A package manager that aims to eliminate the headaches other package managers incur.')
    subParsers = rootParser.add_subparsers(dest = 'command')
    subParsers.required = True
    rootParser.add_argument(
        '--log-level',
        '-l',
        help='importance level cutoff for logging',
        type = str,
        default='info',
        nargs=1
    )
    
    infoParser = subParsers.add_parser('info', help='Fetch info on a package')
    infoParser.set_defaults(function=info)
    infoParser.add_argument(
        'package',
        help='package to operate on',
        type=str
    )

    add_repoParser = subParsers.add_parser('repo', help='Manage package repositories')
    add_repoParser.set_defaults(function=add_repo)
    add_repoParser.add_argument(
        'repository',
        help='repository to add',
        type=str
    )

    docsParser = subParsers.add_parser('docs', help='Get documentation for topics relating to ACP')
    docsParser.set_defaults(function=docs)
    docsParser.add_argument(
        'topic',
        help='topic to search for',
        type=str
    )

    return rootParser.parse_args(argv)

def readConfig(filePath):
    with open(filePath, 'r') as configFile:
        config = json.load(configFile)
    return config

def writeConfig(filePath, config):
    with open(filePath, 'w') as configFile:
        json.dump(config, configFile)


### Commands ###
def info(args, config):
    logger = logging.getLogger('info')
    print('Package information for {}:'.format(args.package))

def add_repo(args, config):
    logger = logging.getLogger('add-repo')
    print('This is where I would add a repo to your local list')

def docs(args, config):
    logger = logging.getLogger('docs')
    logger.debug('fetching docs for {}...'.format(args.topic))
    print('Listing documentation for {}:'.format(args.topic))


### Main program stuffs ###
def main(argv):
    # print(argv)
    args = getArgs(argv[1:])
    # print(args)

    # Ensure that the environment is set up ok
    if not dataDirPath.exists():
        print('Data directory not found, creating one now.')
        dataDirPath.mkdir(parents=True, exist_ok=True)

    if not configPath.exists():
        print('Config file not found, creating one now.')
        configPath.touch()
        writeConfig(configPath, defaultConfig)


    config = readConfig(configPath)

    # Use current setting
    if args.log_level == ['config']:
        logLevel = logLevels[config['log-level']]
    # Override current setting
    else:
        if args.log_level in logLevels.keys():
            logLevel = logLevels[args.log_level]
        else:
            raise ValueError('Invalid log level "{}"'.format(args.log_level))
        
    logging.basicConfig(filename=logPath, filemode='w', level=logLevel)
    
    args.function(args, config)


if __name__ == '__main__':
    main(sys.argv)