# $program = $args[0]
$program = "Logical"
$platform = "win32"
$version = Get-Content "$program.version.txt"

Write-Output "Building $program.exe version $version.$platform..."
nuitka --standalone --include-data-file=Logical.version.txt=Logical.version.txt --include-data-file=LICENSE=LICENSE --include-data-file=README.md=README.md "$program.py" #Build with Nuitka
if ($args -notcontains "--nocleanup") {
    Remove-Item -Recurse -Force "$program.build" #Delete the build directory
}

Remove-Item "dist/$program.$version.$platform" -Recurse -Force -ErrorAction Ignore
Move-Item "$program.dist" "dist/$program.$version.$platform"

Write-Output "Done building $program.exe."