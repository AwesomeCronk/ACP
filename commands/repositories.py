import os, sys

from constants import paths
import utils


def command_add_repo(args, config):
    log = utils.logging.create('add-repo')
    git = utils.dependencies.get('git', log)
    if git is None: exit(1)
    os.chdir(paths.repositories)
    gitOutput = exec(git, 'clone {}'.format(args.repository))  # git clone <args.repository>
    log.debug(gitOutput.decode())

    # git clone new repository
    # confirm that it meets requirements
    # remove it if not

def command_update_repos(args, config):
    log = utils.logging.create('update-repos')
    git = utils.dependencies.get('git', log)
    if args.repository == '<all>':
        log.error('Well you can\'t update all of them at once *yet* ¯\_(ツ)_/¯'); sys.exit(1)
    os.chdir(paths.repositories.joinpath(args.repository))
    gitOutput = exec(git, 'pull origin master')
    log.debug(gitOutput.decode())
