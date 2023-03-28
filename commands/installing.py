import os, shutil, sys

from constants import paths, platform
import operations as ops
import utils


def command_install(args, config):
    log = utils.logging.create('install')
    log.info('Installing {} version {} on {} ({})'.format(args.package, args.version, platform.os, platform.arch))

    # Fetch package data
    packageData, packageFilePath = utils.packages.loadData(args.package, log)
    
    # Identify desired version
    versionToInstall = utils.packages.getExistingVersion(args.version, packageData, log)
    
    # Pick compatible platform
    platforms = packageData['releases'][versionToInstall]['platforms']
    archs = platforms.keys()
    oses = []
    
    if platform.arch in archs:
        oses = platforms[platform.arch]
        arch = platform.arch
    elif 'any' in archs:
        oses = platforms['any']
        arch = 'any'
    else:
        log.error('No install definition for {}'.format(platform.arch)); sys.exit(1)

    if not platform.os in oses.keys():
        log.error('No install definition for {}'.format(platform.os)); sys.exit(1)

    # Install
    if packageData['type'] == 'package_typedef':
        ops.installTypedef('install', packageData, packageFilePath, versionToInstall, arch, platform.os, args.system)
        
    else:
        try:
            ops.installPackage('install', packageData, packageFilePath, versionToInstall, arch, platform.os, args.system)
            print('Installed {}'.format(args.package))
        except ops.UnknownPackageTypeError:
            print('Did not install {}, unknown package type "{}"'.format(packageData['name'], packageData['type']))
