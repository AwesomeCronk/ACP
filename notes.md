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

## Command execution sequence

### install

1. Fetch package data (from file or repository)
2. Pick compatible version/platform
3. If already installed, skip unless --reinstall argument

For package typedefs:

1. Process file and link directories (create dirs, set env vars)
2. Save a copy in `paths.userTypedefs` or `paths.systemTypedefs`

For regular packages:

4. Save to catalog, mark "partially installed"
5. Process files
6. Set up links
7. Save a copy of package file in `paths.userInstalledPackages` or `paths.systemInstalledPackages`
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
