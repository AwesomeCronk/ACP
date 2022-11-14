# AwesomeCronk's Packager
AwesomeCronk's Packager (ACP) is a package manager meant to combat what I see as the biggest flaws in most package managers: Ease of deployment and version management. To achieve this, ACP allows you to install multiple versions of packages and activate multiple versions as you need!

# Usage
More info soon!

### Installing packages:
Different package types will determine where they should be installed and how. You can create package types and assign installation locations for them.

# Installing ACP
Prebuilt binaries are not available as of yet. Compiling is to be done with Nuitka, ideally with Python 3.8.

Compile:
```shell
python3 -m nuitka --standalone --include-data-file=acp.version.txt=acp.version.txt --include-data-file=LICENSE=LICENSE --include-data-file=README.md=README.md acp.py
```

Install (Linux):
```shell
sudo cp -r acp.dist /usr/local/bin/acp.linux
sudo ln -s /usr/local/bin/acp.linux/acp /usr/local/bin/acp
```

Currently, Linux is the only supported platform. Windows support is in the works, but is a ways out. Precompiled binaries, as well as an install script, will be available soon after the first relatively usable release.

# Removing ACP
If you installed ACP and decided you don't like it, it is completely removable. Since an automatic removal tool has not been set up yet, you will have to clean it out manually.

First, package typedefs are stored at `/etc/acp/_package_typedefs` and `~/.local/share/acp/_package_typedefs`. You will have to read these package typedefs to find where different packages were installed, although you should be careful because some typedefs put links in system paths to avoid path modification.

Second, ACP may modify system environment variables when installing package typedefs (NOT IMPLEMENTED YET, SHOULD NOT BE A PROBLEM). `~/.profile` may contain a section labelled `ACP SECTION`, remove that. `/etc/environment`, idk yet.

Last, ACP config and data are stored in these directories:
* `/etc/acp`
* `~/.local/share/acp`
* `/tmp/acp`
