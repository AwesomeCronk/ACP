import shlex, shutil, subprocess


# Dependencies
def get(name, log):
    result = shutil.which(name)
    if result is None:
        log.error('dependency "{}" not found'.format(name))
        return False
    else:
        return result

def exec(path, command):
    proc = subprocess.Popen([path, *shlex.split(command)], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    return ''.join([line.decode() for line in proc.communicate()]).encode()
