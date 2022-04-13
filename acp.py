import argparse, json, logging, os, pathlib, re, requests, shlex, shutil, subprocess, sys
from datetime import datetime


### Constants ###
# Platform
if sys.platform == 'linux':
    if pathlib.Path('/sbin/init').resolve() == pathlib.Path('/usr/lib/systemd/systemd'):
        platform = 'Linux-Systemd'
    else:
        platform = 'Linux-Unknown'
elif sys.platform == 'win32':
    platform = 'Windows'
elif sys.platform == 'darwin':
    platform = 'MacOS'
else:
    platform = 'Unknown'

supportedPlatforms = ('Linux-Systemd',)

# File paths
if platform == 'Linux-Systemd':
    dataDirPath = pathlib.Path('~/.local/share/ACP').expanduser()
    logPath = dataDirPath.joinpath('log.txt')
    configPath = dataDirPath.joinpath('config.json')
    repositoriesPath = dataDirPath.joinpath('repositories')
elif platform == 'Windows':
    raise RuntimeError('Windows is not yet supported - I hope to change that soon!')
else:
    raise RuntimeError('Platform "{}" is not recognized and therefore not supported.'.format(platform))

# URLs
docsRootURL='https://raw.githubusercontent.com/AwesomeCronk/ACP/master/docs/'   # Base url to fetch documentation

# Errors
class ConfigError(Exception):
    pass

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
    rootParser = argparse.ArgumentParser(prog='ACP', description='A package manager that aims to eliminate the headaches other package managers are prone to.')
    rootParser.add_argument(
        '--log-level',
        '-l',
        help='importance level cutoff for logging',
        type = str,
        default=['config'],
        nargs=1
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
        default='latest-stable'
    )
    installParser.add_argument(
        '-l',
        '--location',
        help='location in which to install the package',
        type=pathlib.Path
    )

    platformsParser = subParsers.add_parser('platforms', help='Get supported platforms')
    platformsParser.set_defaults(function=platforms)

    return rootParser.parse_args(argv)

def readConfig(filePath):
    with open(filePath, 'r') as configFile:
        config = json.load(configFile)
    return config

def writeConfig(filePath, config):
    with open(filePath, 'w') as configFile:
        json.dump(config, configFile)

def checkDependency(name, logger):
    result = shutil.which(name)
    if result is None:
        logger.error('dependency "{}" not found'.format(name))
        raise RuntimeError('This operation requires that "{}" is installed and available on PATH.'.format(name))
    else:
        return result

def getURLType(url: str):
    # urlTypes = ('name', 'repo/name', 'web', 'file')
    if url[0] in ('.', '/'):    # Going to need changed for Windows support
        return 'file'
    elif url[0:7] == 'http://' or url[0:8] == 'https://':
        return 'web'
    elif url.count('/') == 0:
        return 'name'
    elif url.count('/') == 1:
        return 'repo/name'
    else:
        return 'unknown'

def getPackageTypes():
    packageTypedefs = {
        'package-typedef':
        {
            'global':
            {
                'install-path': pathlib.Path('<none>'),
                'link-path': pathlib.Path('<none>')
            },
            'local':
            {
                'install-path': dataDirPath.joinpath('_packageTypes'),
                'link-path': pathlib.Path('<none>')
            }
        }
    }

    print(packageTypedefs['package-typedef']['local']['install-path'])
    print(packageTypedefs['package-typedef']['local']['install-path'].glob('*'))
    packageTypedefPaths = packageTypedefs['package-typedef']['local']['install-path'].glob('*')
    for packageTypedefPath in packageTypedefPaths:
        print(packageTypedefPath)

def git(path, command):  # Wrapper for subprocess to facilitate one-line git commands.
    git = subprocess.Popen([path, *shlex.split(command)], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    return ''.join([line.decode() for line in git.communicate()]).encode()


### Commands ###
def info(args, config):
    logger = logging.getLogger('info')
    print('Package information for {}:'.format(args.package))

def add_repo(args, config):
    logger = logging.getLogger('add-repo')
    pathToGit = checkDependency('git', logger)
    os.chdir(repositoriesPath)
    gitOutput = git(pathToGit, 'clone {}'.format(args.repository))
    print(gitOutput.decode())

    # git clone new repository
    # confirm that it meets requirements
    # remove it if not

def update_repos(args, config):
    logger = logging.getLogger('update-repo')
    pathToGit = checkDependency('git', logger)
    if args.repository == '<all>':
        raise NotImplementedError('Well you can\'t update all of them at once yet ¯\_(ツ)_/¯')
    os.chdir(repositoriesPath.joinpath(args.repository))
    gitOutput = git(pathToGit, 'pull origin master')
    print(gitOutput.decode())

def docs(args, config):
    logger = logging.getLogger('docs')
    logger.debug('fetching docs for {}...'.format(args.topic))
    print('Listing documentation for {}:'.format(args.topic))

def platforms(args, config):
    print('The following platforms are currently supported:')
    print('\n'.join([platform for platform in supportedPlatforms]))

def install(args, config):
    logger = logging.getLogger('install')
    logger.info('Attempting to install "{}" version "{}"'.format(args.package, args.version))
    urlType = getURLType(args.package)
    logger.debug('URL type: {}'.format(urlType))

    # Fetch package data
    if urlType == 'name':
        # Search available repositories for package, then fetch package data
        packageData = ''

    elif urlType == 'repo/name':
        # Check specified repo for package, then fetch package data
        repo, name = args.package.split('/')

        foundRepository = False
        for repositoryPath in repositoriesPath.glob('*'):
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

            else:
                raise RuntimeError('Repository "{}" has no entry for package "{}"'.format(repo, name))

        else:
            raise RuntimeError('Could not find repository "{}".'.format(repo))

    elif urlType == 'web':  # HUGE security hazard, may drop in the future
        # Request specified URL to fetch package data
        response = requests.get(args.package)
        
        # May remove this later
        if args.package[-4:] != '.acp':
            raise RuntimeError('Package URL does not have .acp extension.')

        packageData = response.content.decode()

    elif urlType == 'file':
        # Read file to fetch package data
        with open(pathlib.Path(args.package).resolve(), 'r') as file:
            packageData = file.read()

    # Parse package data
    packageData = json.loads(packageData)

    if args.version == 'latest-stable':
        if 'latest-stable' in packageData.keys() and packageData['latest-stable'] != '<none>':
            versionToInstall = packageData['latest-stable']
        else:
            raise RuntimeError('No latest-stable version defined in this package.')

    elif args.version == 'latest':
        if 'latest' in packageData.keys() and packageData['latest'] != '<none>':
            versionToInstall = packageData['latest']
        else:
            raise RuntimeError('No latest version defined in this package.')

    elif args.version in packageData['versions']:
        versionToInstall = args.version

    else:
        raise RuntimeError('Package "{}" has no version "{}".'.format(args.package, args.version))

    if not platform in packageData['versions'][versionToInstall]['platforms'].keys():
        raise RuntimeError('Version "{}" has no platform definition for "{}"'.format(versionToInstall, platform))

    # Install package
    logger.info('Installing package "{}" version "{}"'.format(packageData['name'], versionToInstall))
    print('Name: {}\nType: {}\nAvailable versions: {}'.format(packageData['name'], packageData['type'], ', '.join([v for v in packageData['versions'].keys()])))

    filesData = packageData['versions'][versionToInstall]['platforms'][platform]['files']
    linksData = packageData['versions'][versionToInstall]['platforms'][platform]['links']

    print('Files:')
    for fileData in filesData:
        print(fileData['path'])
    
    print('Links:')
    for linkData in linksData:
        print(linkData['path'])
    
    getPackageTypes()

    print('Installed {}'.format(args.package))


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

    if not repositoriesPath.exists():
        print('Repository directory not found, creating one now.')
        repositoriesPath.mkdir(parents=True, exist_ok=True)


    config = readConfig(configPath)

    # Use current setting
    if args.log_level == ['config']:
        if config['log-level'] in logLevels.keys():
            logLevel = logLevels[config['log-level']]
        else:
            raise ValueError('Invalid log level "{}" from configuration'.format(config['log-level']))
    # Override current setting
    else:
        if args.log_level[0] in logLevels.keys():
            logLevel = logLevels[args.log_level[0]]
        else:
            raise ValueError('Invalid log level "{}"'.format(args.log_level[0]))
        
    logging.basicConfig(filename=logPath, filemode='a', level=logLevel)
    logging.info('=========={}=========='.format(datetime.now().strftime('%Y-%m-%d %H:%M')))
    
    args.function(args, config)


if __name__ == '__main__':
    main(sys.argv)