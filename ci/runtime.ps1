param([string]$Variant)
$ErrorActionPreference = 'Stop'
$entry = (Get-Content ci/runtime-packages.json -Raw | ConvertFrom-Json).$Variant
if ($entry.subdir -eq 'win-arm64' -and [System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture -ne 'Arm64') { throw 'Expected native ARM64 OS' }
Invoke-WebRequest https://github.com/mamba-org/micromamba-releases/releases/download/1.5.10-0/micromamba-win-64 -OutFile "$env:RUNNER_TEMP\micromamba.exe"
gh run download $entry.run --repo ClayWarren/pywinpty-feedstock --name $entry.artifact --dir C:\runtime-artifacts
if ($LASTEXITCODE -ne 0) { throw 'Artifact download failed' }
$channel = 'C:\runtime-channel'
New-Item -ItemType Directory -Path "$channel\$($entry.subdir)","$channel\noarch" -Force | Out-Null
$records = @{}
foreach ($package in $entry.packages) {
    $files = @(Get-ChildItem C:\runtime-artifacts -Recurse -File -Filter $package.file)
    if ($files.Count -ne 1) { throw "Expected one artifact for $($package.file)" }
    if ((Get-FileHash $files[0].FullName -Algorithm SHA256).Hash.ToLower() -ne $package.record.sha256) { throw 'Package checksum mismatch' }
    Copy-Item $files[0].FullName "$channel\$($entry.subdir)\$($package.file)"
    $records[$package.file] = $package.record
}
@{info=@{subdir=$entry.subdir};packages=@{};'packages.conda'=$records;removed=@();repodata_version=1} | ConvertTo-Json -Depth 20 | Set-Content "$channel\$($entry.subdir)\repodata.json" -Encoding utf8
@{info=@{subdir='noarch'};packages=@{};'packages.conda'=@{};removed=@();repodata_version=1} | ConvertTo-Json -Depth 20 | Set-Content "$channel\noarch\repodata.json" -Encoding utf8
$env:CONDA_SUBDIR = $entry.subdir
& "$env:RUNNER_TEMP\micromamba.exe" create -y -p C:\pywinpty-runtime --strict-channel-priority --override-channels -c file:///C:/runtime-channel -c conda-forge -c conda-forge/label/python_rc "python=$($entry.python)" pywinpty
if ($LASTEXITCODE -ne 0) { throw 'Fresh runtime install failed' }
& "$env:RUNNER_TEMP\micromamba.exe" run -p C:\pywinpty-runtime python -u recipe/run_test.py
if ($LASTEXITCODE -ne 0) { throw 'Installed runtime tests failed' }
