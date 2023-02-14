import pathlib, shutil, sys

from constants import paths
import utils


class UnknownPackageTypeError(Exception): pass


def installTypedef(caller, source, sourcePath, version, arch, os, system):
    log = utils.logging.create('installTypedef')
    log.info('Installing typedef for {}'.format('whole system' if system else 'current user'))

    files = source['releases'][version]['platforms'][arch][os]['files']
    links = source['releases'][version]['platforms'][arch][os]['links']

    for file in files:
        if file['source'] == ('system' if system else 'user'):
            utils.filesys.processTypedefFile(file, log)

    for link in links:
        if link['source'] == ('system' if system else 'user'):
            utils.filesys.processTypedefFile(link, log)
            
    # Make a copy of the typedef file to be available for installing packages later
    targetPath = (paths.systemData if system else paths.userTypedefs).joinpath(sourcePath.name)
    
    log.debug('Copying {} to {}'.format(sourcePath, targetPath))
    with open(sourcePath, 'rb') as sourceFile:
        with open(targetPath, 'wb') as targetFile:
            targetFile.write(sourceFile.read())

def installPackage(caller, source, sourcePath, version, arch, os, system):
    log = utils.logging.create('installPackage')
    log.info('Installing package for {}'.format('whole system' if system else 'current user'))
    
    # Load system typedefs and then optionally user typedefs
    packageTypedefs = utils.packages.loadTypedefs('system', log)
    if not system: packageTypedefs.update(utils.packages.loadTypedefs('user', log))
    log.debug('Available package typedefs: {}'.format(', '.join(list(packageTypedefs.keys()))))

    if not source['type'] in packageTypedefs.keys():
        raise UnknownPackageTypeError()

    versionTag = (version).replace('.', packageTypedefs[source['type']]['version_separator'])

    fileDir = packageTypedefs[source['type']]['files']['system' if system else 'user']
    fileDir = fileDir.joinpath(source['name']).joinpath(version)
    linkDir = packageTypedefs[source['type']]['links']['system' if system else 'user']

    files = source['releases'][version]['platforms'][arch][os]['files']
    links = source['releases'][version]['platforms'][arch][os]['links']

    # Remove previous installation (same version only)
    try:
        shutil.rmtree(fileDir)
        log.debug('Deleted previous identical installation')
    except:
        pass

    for link in links:
        try: linkDir.joinpath(link['name'] + versionTag).unlink()
        except: pass
        try: linkDir.joinpath(link['name']).unlink()
        except: pass

    utils.filesys.ensureDirExists(fileDir)

    for file in files:
        processPackageFile(file, fileDir, log)

    for link in links:
        # Version specific links
        linkPath = linkDir.joinpath(link['name'] + versionTag)
        targetPath = fileDir.joinpath(link['target'])
        log.info('Linking {} to {}'.format(linkPath, targetPath))
        linkPath.symlink_to(targetPath)
    activatePackage(caller, source, sourcePath, version, arch, os, system)

def activatePackage(caller, source, sourcePath, version, arch, os, system):
    log = utils.logging.create('activatePackage')
    log.info('Activating package for {}'.format('whole system' if system else 'current user'))

    # Load system typedefs and then optionally user typedefs
    packageTypedefs = utils.packages.loadTypedefs('system', log)
    if not system: packageTypedefs.update(utils.packages.loadTypedefs('user', log))
    log.debug('Available package typedefs: {}'.format(', '.join(list(packageTypedefs.keys()))))
    
    versionTag = ('.' + version).replace('.', packageTypedefs[source['type']]['version_separator'])

    linkDir = packageTypedefs[source['type']]['links']['system' if system else 'user']
    
    links = source['releases'][version]['platforms'][arch][os]['links']

    for link in links:
        # Regular links
        linkPath = linkDir.joinpath(link['name'])
        targetPath = linkDir.joinpath(link['name'] + versionTag)
        log.info('Linking {} to {}'.format(linkPath, targetPath))
        linkPath.symlink_to(targetPath)

def processTypedefFile(file, log):
    log.debug('Processing {} (action: {})'.format(file['path'], file['action']))
    for action in file['action'].split(';'):
        if action.strip() == '': continue
        command, *args = action.strip().split()

        if command == 'ensure':
            log.debug('Ensuring existence')
            utils.ensureDirExists(pathlib.Path(file['path']))

        elif command == 'modvars':
            log.debug('!Modifying system environment variable {}'.format(args[0]))

        elif command == 'modvaru':
            log.debug('!Modifying user environment variable {}'.format(args[0]))

def processPackageFile(file, fileDir, log):
    global _7zip

    for action in file['action'].split(';'):
        if action.strip() == '': continue
        command, *args = action.strip().split()

        # Write a file
        if command == 'write':
            filePath = fileDir.joinpath(file['path'])
            log.info('Writing {}'.format(filePath))
            with open(filePath, 'wb') as destFile:
                destFile.write(utils.packages.readSource(file['source'], log))
            if len(args):
                try:
                    log.info('Setting permissions to {}'.format(args[0]))
                    filePath.chmod(int('0o' + args[0], base=8))
                except ValueError:
                    log.warning('Specified permissions invalid, did not set permissions')
        
        # Extract a .7z archive
        elif command == '7zip':
            log.info('!Extracting 7zip archive')
            _7zip = utils.dependencies.get('7z', log)
            if _7zip is None: sys.exit(1)
            utils.ensureDirExists(paths.temp, log)
            archivePath = paths.temp.joinpath('archive.7z')
            with open(archivePath, 'wb') as archiveFile:
                archiveFile.write(utils.readSource(file['source'], log))
            _7zipArgs = 'x -o{} {}'.format(file['path'], archivePath)
            log.debug(_7zipArgs)
            exec(_7zip, _7zipArgs)
