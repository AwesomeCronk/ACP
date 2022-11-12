import logging, os, shutil

from constants import logNameLen
from utils import *


def info(args, config):
    log = logging.getLogger('info')
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

def add_repo(args, config):
    log = logging.getLogger('add-repo')
    log.setLevel(logging.DEBUG)
    log.addHandler(logStreamHandler)
    log.addHandler(logFileHandler)
    git = getDependency('git', log)
    if git is None: exit(1)
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
    log = logging.getLogger('install'.ljust(logNameLen))
    log.setLevel(logging.DEBUG)
    log.addHandler(logStreamHandler)
    log.addHandler(logFileHandler)
    log.info('Attempting to install {} version {} on {} ({})'.format(args.package, args.version, platform.os, platform.arch))

    # Fetch package data
    packageData, packageFilePath = loadPackageData(args.package)
    packageTypedefs = loadPackageTypedefs('system')
    if not args.system: packageTypedefs.update(loadPackageTypedefs('user'))
    log.debug('Available package typedefs: {}'.format(', '.join(list(packageTypedefs.keys()))))

    # Version picking
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

    # Platform picking
    platforms = packageData['releases'][versionToInstall]['platforms']
    archs = platforms.keys()
    oses = None
    if platform.arch in archs:
        oses = platforms[platform.arch]
    elif 'any' in archs:
        oses = platforms['any']
    else: log.error('No install definition for {}'.format(platform.arch)); sys.exit(1)

    if (not oses is None) and platform.os in oses.keys():
        files = oses[platform.os]['files']
        links = oses[platform.os]['links']
    else: log.error('No install definition for {}'.format(platform.os)); sys.exit(1)

    # Install typedef
    if packageData['type'] == 'package_typedef':
        sourcePath = packageFilePath

        def _processFile(file, isLink=False):
            log.debug('Processing {} (action: {})'.format(file['path'], file['action']))
            for action in file['action'].split(';'):
                if action.strip() == '': continue
                command, *args = action.strip().split()

                if command == 'ensure':
                    log.debug('Ensuring existence')
                    ensureDirExists(pathlib.Path(file['path']))

                elif command == 'modvars':
                    log.debug('!Modifying system environment variable {}'.format(args[0]))

                elif command == 'modvaru':
                    log.debug('!Modifying user environment variable {}'.format(args[0]))

        log.info('Installing typedef for {}'.format('whole system' if args.system else os.getlogin()))
        targetPath = (paths.systemData if args.system else paths.userData).joinpath('_package_typedefs').joinpath(packageFilePath.name)

        for file in files:
            if file['source'] == ('system' if args.system else 'user'):
                _processFile(file)
        for link in links:
            if link['source'] == ('system' if args.system else 'user'):
                _processFile(link, True)
                
        # Make a copy of the typedef file to be available for installing packages later
        log.debug('Copying {} to {}'.format(sourcePath, targetPath))
        with open(sourcePath, 'rb') as sourceFile:
            with open(targetPath, 'wb') as targetFile:
                targetFile.write(sourceFile.read())

    # Install regular package
    elif packageData['type'] in packageTypedefs.keys():
        fileDir = packageTypedefs[packageData['type']]['files']['system' if args.system else 'user']
        fileDir = fileDir.joinpath(packageData['name']).joinpath(versionToInstall)
        linkDir = packageTypedefs[packageData['type']]['links']['system' if args.system else 'user']
        
        if fileDir.is_dir():
            log.info('Detected previous installation, removing it')
            shutil.rmtree(fileDir)
        ensureDirExists(fileDir)

        def _processFile(file, isLink=False):
            if isLink:
                link = file
                linkPath = linkDir.joinpath(link['name'])
                targetPath = fileDir.joinpath(link['target'])
                log.info('Linking {} to {}'.format(linkPath, targetPath))
                linkPath.symlink_to(targetPath)

            else:
                for action in file['action'].split(';'):
                    if action.strip() == '': continue
                    command, *args = action.strip().split()

                    if command == 'write':
                        filePath = fileDir.joinpath(file['path'])
                        log.info('Writing {}'.format(filePath))
                        with open(filePath, 'wb') as destFile:
                            destFile.write(readSource(file['source']))
                    
                    elif command == '7z':
                        log.info('!Running 7zip ({})'.format(args))

        for file in files:
            _processFile(file)
        
        for link in links:
            _processFile(link, True)

        print('Installed {}'.format(args.package))

    else:
        print('Did not install {}, unknown package type "{}"'.format(packageData['name'], packageData['type']))
