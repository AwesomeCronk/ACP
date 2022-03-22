# Packages
A package file is a [JSON](https://en.wikipedia.org/wiki/JSON) file containing information on the package such as available versions, where to find the files for them, etc.

## JSON Structure
This is an example structure showing necessary entries in package files.
```json
{
    "name": "uPyFile",
    "type": "program",
    "releases":
    [
        {
            "version": "1.4.0",
            "platform": "linux",
            "files":
            [
                {"path": "upyfile", "source": "https://raw.githubusercontent.com/AwesomeCronk/uPyFile/master/upyfile", "action": "write"},
                {"path": "LICENSE", "source": "https://raw.githubusercontent.com/AwesomeCronk/uPyFile/master/LICENSE", "action": "write"},
                {"path": "README.md", "source": "https://raw.githubusercontent.com/AwesomeCronk/uPyFile/master/README.md", "action": "write"}
            ]
        }
    ]
}
```
*Please note, the URLs used for the file sources here link to the most recent version on GitHub. This is, in practice, a very bad way to get files, but I had no better example on hand. I will change this for a better example soon.*

## Required Fields
Package files contain a JSON dict requiring a `name`, the `type` of package, and a list of `releases`. Releases require a `version`, the associated `platform`, and a list of `files`. Files require the `path` in which they will be installed, the `source` from which ACP should fetch them, and the `action` for ACP to take with them.

### Platform
A release's platform specification should be one of the supported platforms, as presented when running `acp platforms`.

### Path
The path a file will be installed to should be presented as a valid path for the platform the release is meant for. Paths should be relative and should reside in the package directory. (`../../file` should not be used as a means to get the file installed somewhere other than the package directory.)

### Source
A file's source should be permanent and unchanging. This means that (unlike the example above) you should not link to the "active development" version of the file. The URL for files should be fetchable via HTTPS GET, and should return the raw content of the file.