import pathlib, requests, sys

from constants import paths
from utils import dependencies


# Filesystem interaction
def processTypedefFile(file, log):
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
                destFile.write(readSource(file['source'], log))
            if len(args):
                try:
                    log.info('Setting permissions to {}'.format(args[0]))
                    filePath.chmod(int('0o' + args[0], base=8))
                except ValueError:
                    log.warning('Specified permissions invalid, did not set permissions')
        
        # Extract a .7z archive
        elif command == '7zip':
            log.info('!Extracting 7zip archive')
            _7zip = dependencies.get('7z', log)
            if _7zip is None: sys.exit(1)
            ensureDirExists(paths.temp, log)
            archivePath = paths.temp.joinpath('archive.7z')
            with open(archivePath, 'wb') as archiveFile:
                archiveFile.write(readSource(file['source'], log))
            _7zipArgs = 'x -o{} {}'.format(file['path'], archivePath)
            log.debug(_7zipArgs)
            exec(_7zip, _7zipArgs)

def ensureFileExists(path):
    path = path.expanduser()
    # Does not overwrite existing files
    if path.is_file():
        return

    elif path.is_dir():
        raise FileExistsError('A directory exists at {}, cannot create file there.'.format(path))

    else:
        file = open(path, 'a'); file.close()

def ensureDirExists(path):
    path = path.expanduser()
    # Does not overwrite existing directories
    if path.is_dir():
        return

    else:
        path.mkdir(parents=True, exist_ok=False)    # Don't catch FileExistsError here, let it propagate.

def readSource(url, log):
    if url[0:8] == 'https://' or url[0:7] == 'http://':
        try:
            resp = requests.get(url)
        except requests.exceptions.ConnectionError:
            log.error('Unable to connect to remote host ({})'.format(url)); sys.exit(1)
        if resp.ok == False:
            log.error('Request failed, code {} ({})'.format(resp.status_code, url)); sys.exit(1)
        data = resp.content
    
    else:
        try:
            with open(url, 'rb') as file:
                data = file.read()
        except FileNotFoundError:
            log.error('File not found ({})'.format(url)); sys.exit(1)
    
    return data
