For environment variables on linux, use /etc/environment or ~/.profile.

Any printouts prefixed with `!` indicate that ACP is skimming over unimplemented functionality. Usually this is to help lay out program flow from the top down.

## System file structure

* Package files dir (user/system)
  * packageA files dir
  * packageB files dir
* Package links dir (user/system)
  * Links associated with user packages
* ACP data dir (user/system)
  * config.json5
  * log.txt (user only)
  * _package_typedefs
  * repositories
  * catalog.json5

## Repository file structure

All files that end in `.acp` are processed as package files when searching a repository. The file name (minus the `.acp` at the end) must match the pakcage name it represents. Additional files may be present, such as `LICENSE` and `README.md`, but no file that should not be interpreted as a package file may have a name ending in `.acp`.

## Command execution sequence

### install

1. Fetch package data (from file or repository)
2. If from file, copy the file to sourcefiles repository
3. Pick compatible version/platform
4. If already installed, skip unless --reinstall argument

For package typedefs:

5. Process file and link directories (create dirs, set env vars)
6. Save a copy in `paths.userTypedefs` or `paths.systemTypedefs`  (use package name, not file name)

For regular packages:

5. Save to catalog, mark "partially installed"
6. Process files
7. Set up links
8. Mark "installed" in catalog

### uninstall

1. Fetch typedef from catalog
2. Pick version to uninstall

For package typedefs:

For regular packages:


### add-repo

1. Clone repository
2. 

### update-repos

### info

### docs

### paths

1. List all objects in `paths` that don't begin with `__` and are not `forbiddenChars`
