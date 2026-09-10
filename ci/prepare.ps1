$ErrorActionPreference = 'Stop'
$arch = [System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture
if ($arch -ne 'Arm64') { throw "Expected ARM64 OS, got $arch" }
Write-Host "Native OS: $arch"
Invoke-WebRequest https://github.com/mamba-org/micromamba-releases/releases/download/1.5.10-0/micromamba-win-64 -OutFile "$env:RUNNER_TEMP\micromamba.exe"
New-Item -ItemType Directory -Path C:\pywinpty-local\win-arm64 -Force | Out-Null

gh run download 34442235176 --repo ClayWarren/pywinpty-feedstock --name pywinpty-win-arm64 --dir C:\pywinpty-local\win-arm64
if ($LASTEXITCODE -ne 0) { throw 'Could not download validated winpty prerequisite' }
$package = 'C:\pywinpty-local\win-arm64\winpty-0.4.3-hef4af3d_4.conda'
if ((Get-FileHash $package -Algorithm SHA256).Hash.ToLower() -ne '4d68ce92a2fd4e224d43b734c088e31a2262b6d2cb00c1e932cc15b31c11b80c') { throw 'Winpty prerequisite checksum mismatch' }
