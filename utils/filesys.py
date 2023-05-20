# Filesystem interaction
def ensureFileExists(path):
    path = path.expanduser()
    # Does not overwrite existing files
    if path.is_file():
        return

    elif path.is_dir():
        raise FileExistsError('A directory exists at {}, cannot create file'.format(path))

    else:
        file = open(path, 'a'); file.close()

def ensureDirExists(path):
    path = path.expanduser()
    # Does not overwrite existing directories
    if path.is_dir():
        return

    else:
        path.mkdir(parents=True, exist_ok=False)    # Don't catch FileExistsError here, let it propagate
