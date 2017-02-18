function CopyPrebuiltDLLs () {
    $target = "x86"
    if ($env:PYTHON_ARCH -eq "64") {
        $target = "x64"
    }
    $prebuilt_dir = "prebuilt-"+$target

    $basedir = $pwd.Path + "\"
    $dlls = $basedir + $prebuilt_dir + "\lib\" + "*.dll"
    $destpath = $basedir + "pygame"

    Write-Host "dlls from" $dlls
    Write-Host "destiation" $destpath

    Copy-item $dlls -destination $destpath
}

function main () {
    CopyPrebuiltDLLs
}

main
