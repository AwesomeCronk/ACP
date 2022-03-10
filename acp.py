import argparse, pathlib, logging, sys
from asyncio.log import logger

platform = sys.platform

if platform == 'linux':
    logPath = pathlib.Path('~/.local/share/ACP/log.txt').expanduser()
    configPath = pathlib.Path('~/.local/share/ACP/config.json').expanduser()

docsURL='https://raw.githubusercontent.com/AwesomeCronk/ACP/master/docs'


def getArgs(null):
    rootParser = argparse.ArgumentParser(prog='ACP', description='A package manager that aims to eliminate the headaches other package managers incur.')
    subParsers = rootParser.add_subparsers()
    
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

    return rootParser.parse_args()

def readConfig(key, value):
    pass

def writeConfig(key, value):
    pass


def info(args):
    logger = logging.getLogger('info')
    print('Package information for {}:'.format(args.package))

def add_repo(args):
    logger = logging.getLogger('add-repo')
    print('This is where I would add a repo to your local list')

def docs(args):
    logger = logging.getLogger('docs')
    logger.debug('fetching docs for {}...'.format(args.topic))
    print('Listing documentation for {}:'.format(args.topic))


def main(argv):
    args = getArgs(argv)
    args.function(args)


if __name__ == '__main__':
    main(sys.argv)