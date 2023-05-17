from constants import paths
import utils


def command_docs(args, config):
    log = utils.logging.create('docs')
    log.debug('Fetching docs for {}...'.format(args.topic))
    print('Listing documentation for {}:'.format(args.topic))

def command_paths(args, config):
    log = utils.logging.create('paths')
    nameLen = 0
    output = []
    for path in dir(paths):
        if path[0:2] != '__' and path != 'forbiddenChars':
            nameLen = max(nameLen, len(path))
            output.append((path, getattr(paths, path)))

    packageTypedefs = utils.packages.loadTypedefs('system', log)
    packageTypedefs.update(utils.packages.loadTypedefs('user', log))

    for packageType in packageTypedefs.keys():
        for context in packageTypedefs[packageType]['files'].keys():
            pathName = packageType + ' {} files'.format(context)
            nameLen = max(nameLen, len(pathName))
            output.append((pathName, packageTypedefs[packageType]['files'][context]))

        for context in packageTypedefs[packageType]['links'].keys():
            pathName = packageType + ' {} links'.format(context)
            nameLen = max(nameLen, len(pathName))
            output.append((pathName, packageTypedefs[packageType]['links'][context]))

    for name, path in output:
        print('{} : {}'.format(name.rjust(nameLen), path))