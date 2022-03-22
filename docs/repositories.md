# Repositories
An ACP repository is a Git repository suitable as a remote repository (not local). (Essentially anything you would be able to see when you run `git remote` in a local repository.) ACP repositories should have the following directory structure:
* `<repository name>`
  * `packages`
  * `description.txt`
  * `README.md` (optional)

### `packages`
This is a directory containing `<package>.json` files used by ACP when installing software. See [Packages](https://github.com/AwesomeCronk/ACP/docs/packages.md) for info on what goes in these files.

### `description.txt`
This file contains the short description of the repository. It is fetched and printed whenever `acp repository <repository-name> --info` is run.

### `README.md`
This file explains what's up with the repository, what makes it special, etc. You can put whatever you like here, but note that it will only be read when people visit the repository itself.