import logging, os, requests
import json5

from utils import *


def info(args, config):
    log = logging.getLogger('info')
    log.setLevel(logging.DEBUG)
    log.addHandler(logStreamHandler)
    log.addHandler(logFileHandler)
    print('Package information for {}:'.format(args.package))

def add_repo(args, config):
    log = logging.getLogger('add-repo')
    log.setLevel(logging.DEBUG)
    log.addHandler(logStreamHandler)
    log.addHandler(logFileHandler)
    git = getDependency('git', log)
    os.chdir(paths.repositories)
    gitOutput = exec(git, 'clone {}'.format(args.repository))  # git clone <args.repository>
    log.debug(gitOutput.decode())

    # git clone new repository
    # confirm that it meets requirements
    # remove it if not

def update_repos(args, config):
    log = logging.getLogger('update-repo')
    log.setLevel(logging.DEBUG)
    log.addHandler(logStreamHandler)
    log.addHandler(logFileHandler)
    git = getDependency('git', log)
    if args.repository == '<all>':
        log.error('Well you can\'t update all of them at once *yet* ¯\_(ツ)_/¯'); sys.exit(1)
    os.chdir(paths.repositories.joinpath(args.repository))
    gitOutput = exec(git, 'pull origin master')
    log.debug(gitOutput.decode())

def docs(args, config):
    log = logging.getLogger('docs')
    log.setLevel(logging.DEBUG)
    log.addHandler(logStreamHandler)
    log.addHandler(logFileHandler)
    log.debug('Fetching docs for {}...'.format(args.topic))
    print('Listing documentation for {}:'.format(args.topic))

def install(args, config):
    log = logging.getLogger('install')
    log.setLevel(logging.DEBUG)
    log.addHandler(logStreamHandler)
    log.addHandler(logFileHandler)
    log.info('Attempting to install "{}" version "{}"'.format(args.package, args.version))

    # Fetch package data
    packageData = loadPackageData(args.package)

    packageTypedefs = loadPackageTypes()

    if packageData['type'] == 'package-typedef':
        if platform in packageData['releases']['global']['platforms'].keys():
            pass
            # Get file and link locations for defined package type and create them
            # Get install location for package-typedefs from packageTypedefs['package-typedef'] and copy package file there

    else:
        if args.version == 'latest_stable':
            if not packageData['latest_stable'] is None:
                versionToInstall = packageData['latest_stable']
            else: log.error('No latest_stable version defined in this package.'); sys.exit(1)

        elif args.version == 'latest':
            if not packageData['latest'] is None:
                versionToInstall = packageData['latest']
            else: log.error('No latest version defined in this package.'); sys.exit(1)

        elif args.version in packageData['releases']:
            versionToInstall = args.version

        else: log.error('Package "{}" has no version "{}".'.format(args.package, args.version)); sys.exit(1)

        platforms = packageData['releases'][versionToInstall]['platforms']
        archs = platforms.keys()
        if platform.arch in archs:
            oses = platforms[platform.arch]
            if platform.os in oses.keys():
                files = oses[platform.os]['files']
                links = oses[platform.os]['links']

            else: log.error('No install definition for {}'.format(platform.os)); sys.exit(1)
        else: log.error('No install definition for {}'.format(platform.arch)); sys.exit(1)

        # Install package
        log.info('Installing package "{}" version "{}"'.format(packageData['name'], versionToInstall))
        log.debug('Name: {}\nType: {}\nAvailable versions: {}'.format(packageData['name'], packageData['type'], ', '.join([v for v in packageData['releases'].keys()])))


        print('Files:')
        for fileData in files:
            print('-', fileData['path'])
        
        print('Links:')
        for linkData in links:
            print('-', linkData['name'])

    print('Installed {}'.format(args.package))
