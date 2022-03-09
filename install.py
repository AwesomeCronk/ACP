import os, shutil, sys

applicationName = 'ACP'
installerVersion = '1.0.0'
downloadDir = os.path.dirname(os.path.realpath(sys.argv[0]))

applicationVersions = [str.join('.', folder.split('.')[1:]) for folder in os.listdir(os.path.join(downloadDir, 'dist')) if folder.split('.')[0] == applicationName]
applicationVersion = sorted(applicationVersions)[-1] # Last entry is highest version number

srcDir = os.path.join(downloadDir, os.path.join('dist', '{}.{}'.format(applicationName, applicationVersion)))

class directory():
    def __init__(self, src, dest, files, overwrite):
        self.src = src
        self.dest = dest
        self.files = files
        self.overwrite = overwrite

# This is the listing of directories to modify.
# Set it up as a dictionary of {name: directory(src, dest, files, overwrite)}
directories = {
    'install': directory(
        srcDir,
        os.path.expandvars('%USERPROFILE%\\AppData\\Local\\Programs\\ACP.'.format(applicationVersion)) if sys.platform == 'win32' else '/usr/local/bin/ACP.{}'.format(applicationVersion),
        os.listdir(srcDir),
        overwrite = True
        )
    }

def version():
    print('Using {} installer version {}.'.format(applicationName, installerVersion))

if len(sys.argv) > 1:
    if sys.argv[1] == 'version':
        version()
else:
    for k in list(directories.keys()):
        print('Processing directory {}.'.format(k))
        d = directories[k]

        if os.path.exists(d.dest):
            if d.overwrite:
                print('Removing directory {}.'.format(d.dest))
                shutil.rmtree(d.dest)
            else:
                print('Directory {} already exists and not set to overwrite. Ignoring.'.format(d.dest))
                continue
        
        # Create d.dest
        print('Creating directory {}.'.format(d.dest))
        os.mkdir(d.dest)

        # copy the necessary files to d.dest
        for file in d.files:
            # print('Copying {} to {} ... '.format(os.path.join(d.src, file), d.dest), end = '')
            print(file)
            if os.path.isdir(os.path.join(d.src, file)):
                shutil.copytree(os.path.join(d.src, file), os.path.join(d.dest, file), dirs_exist_ok=True)
            else:
                shutil.copy(os.path.join(d.src, file), d.dest)
            # print('Done.')