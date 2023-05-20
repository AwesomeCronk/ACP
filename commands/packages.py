import shutil

from constants import paths, platform
import operations as ops
import utils


def command_install(args, config):
    log = utils.logging.create('install')
    log.info('Requested installation of {} version {} on {} ({})'.format(args.package, args.version, platform.os, platform.arch))

    # Fetch package data
    packageData, packageFilePath = utils.packages.loadData(args.package, log)
    packageName = packageData['name']

    # Copy to _sourcefiles repository if installing from a plain file
    if utils.packages.getURLType(args.package) == 'file':
        newPackageFilePath = paths.repositories.joinpath('_sourcefiles/{}.acp'.format(packageName))
        shutil.copy(packageFilePath, newPackageFilePath)
        packageFilePath = newPackageFilePath
    
    # Identify desired version and pick compatible platform
    versionToInstall = utils.packages.getExistingVersion(args.version, packageData, log)
    platformToUse = utils.packages.getCompatiblePlatform(packageData, versionToInstall, log)

    # Install
    log.info('Installing {} version {} on {} ({})'.format(packageName, versionToInstall, platformToUse.os, platformToUse.arch))

    if packageData['type'] == 'package_typedef':
        ops.installTypedef('install', packageData, packageFilePath, versionToInstall, platformToUse, args.system)
    
    else:
        try:
            ops.installPackage('install', packageData, packageFilePath, versionToInstall, platformToUse, args.system)
            print('Installed {}'.format(args.package))
    
        except ops.UnknownPackageTypeError:
            print('Did not install {}, unknown package type "{}"'.format(packageData['name'], packageData['type']))

    ops.activatePackage('install', packageData, packageFilePath, versionToInstall, platformToUse, args.system)


def command_info(args, config):
    log = utils.logging.create('info')

    packageData, packageFilePath = utils.packages.loadData(args.package, log)
    packageTypedefs = utils.packages.loadTypedefs('system', log)
    packageTypedefs.update(utils.packages.loadTypedefs('user', log))
    installedVersions = utils.packages.getInstalledVersions(packageData, packageTypedefs[packageData['type']], log)
    activeVersion = utils.packages.getActiveVersion(packageData, packageTypedefs[packageData['type']], installedVersions, log)

    output = '\n'.join([
        'Information listing for {}:'.format(packageData['name']),
        'Type:                  {}'.format(packageData['type']),
        'Latest release:        {}'.format(packageData['latest']),
        'Latest stable release: {}'.format(packageData['latest_stable']),
        'Active version:        {}'.format(activeVersion),
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
