For environment variables on linux, use /etc/environment or ~/.profile.

Let b-fuze (Mike32)#9778 on Ubuntu Hideout know if you can update variables without logging in/out.

For adding package type definitions install them as a `package-typedef` package. Store the files in `package-types` next to `config.json`.

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
2. Check compatibility

For regular packages:

3. Save to catalog, mark "partially installed"
4. Process files
5. Set up links
6. Store 
7. Mark "installed" in catalog

For package typedefs:

3. Process file and link directories (create dirs, set env vars)
4. Save a copy in `paths.userTypedefs` or `paths.systemTypedefs`

### add-repo

### update-repos

### info

### docs

### paths

1. List all objects in `paths` that don't begin with `__` and are not `forbiddenChars`
