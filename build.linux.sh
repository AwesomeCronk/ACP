#!/bin/bash

# program = $1
program="Logical"
platform='linux'    # Determine platform
version=$(cat "$program.version.txt")

echo "Building $program version $version.$platform..."
python3.9 -m nuitka --standalone --include-data-file=Logical.version.txt=Logical.version.txt --include-data-file=LICENSE=LICENSE --include-data-file=README.md=README.md --include-data-dir=keys=keys "$program.py" #Build with Nuitka

while test $# -gt 0
do
    case "$1" in
        "--nocleanup") rm -rf "$program.build"    #Delete the build directory
        ;;
    esac
    shift
done

# Delete recursively, force through any trivial issues, and skip if the folder does not exist
rm "dist/$program.$version.$platform" -rf
mv "$program.dist" "dist/$program.$version.$platform"

echo "Done building $program."  # $program.exe on Windows
