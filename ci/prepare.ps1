$ErrorActionPreference = 'Stop'
$arch = [System.Runtime.InteropServices.RuntimeInformation]::OSArchitecture
if ($arch -ne 'Arm64') { throw "Expected ARM64 OS, got $arch" }
Write-Host "Native OS: $arch"
Invoke-WebRequest https://github.com/mamba-org/micromamba-releases/releases/download/1.5.10-0/micromamba-win-64 -OutFile "$env:RUNNER_TEMP\micromamba.exe"
New-Item -ItemType Directory -Path C:\pywinpty-local\win-arm64 -Force | Out-Null
