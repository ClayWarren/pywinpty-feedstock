@echo on
set "CONDA_SUBDIR=win-64"
"%RUNNER_TEMP%\micromamba.exe" create -y -p C:\pywinpty-tools -c conda-forge conda-build conda-index
if errorlevel 1 exit /b 1
call C:\pywinpty-tools\condabin\conda.bat activate C:\pywinpty-tools
if errorlevel 1 exit /b 1
set "CONDA_CHANNEL_PRIORITY=strict"
conda build recipe -m .ci_support\win_64_python3.14.____cp314.yaml --croot C:\pywinpty-build --output-folder C:\pywinpty-local --no-anaconda-upload --override-channels -c conda-forge
if errorlevel 1 exit /b 1
