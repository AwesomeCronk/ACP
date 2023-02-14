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
    if args.version == 'latest_stable':
        if not packageData['latest_stable'] is None:
            versionToInstall = packageData['latest_stable']
        else:
            log.error('No latest_stable version defined in this package.'); sys.exit(1)

    elif args.version == 'latest':
        if not packageData['latest'] is None:
            versionToInstall = packageData['latest']
        else:
            log.error('No latest version defined in this package.'); sys.exit(1)

    elif args.version in packageData['releases']:
        versionToInstall = args.version

    else: log.error('Package "{}" has no version "{}".'.format(args.package, args.version)); sys.exit(1)

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
