from constants import paths
import utils


def command_info(args, config):
    log = utils.logging.create('info')

    packageData, packageFilePath = utils.packages.loadData(args.package, log)
    packageTypedefs = utils.packages.loadTypedefs('system', log)
    packageTypedefs.update(utils.packages.loadTypedefs('user', log))
    installedVersions = utils.packages.getInstalledVersions(packageData, packageTypedefs[packageData['type']], log)
    activeVersion = utils.packages.getActiveVersion(packageData, packageTypedefs[packageData['type']], installedVersions, log)

    output = '\n'.join([
        'Information for {}:'.format(packageData['name']),
        'Type: {}'.format(packageData['type']),
        'Latest release: {}'.format(packageData['latest']),
        'Latest stable release: {}'.format(packageData['latest_stable']),
        'Active version: {}'.format(activeVersion),
        'Releases:'
    ])

    # Build output string before printing
    for release in packageData['releases'].keys():
        if args.version == release or args.version == '<all>':
            output += '\n* {}'.format(release)
            if packageData['releases'][release]['stable']: output += ' (stable)'
            if release in installedVersions: output += ' (installed)'
            output += '\n  Release notes: {}'.format(packageData['releases'][release]['release_notes'])
            output += '\n  Platforms:'
            for platform in packageData['releases'][release]['platforms'].keys():
                output += '\n  * {} ({})'.format(platform, ', '.join([os for os in packageData['releases'][release]['platforms'][platform].keys()]))

    print(output)

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