if "%target_platform%"=="win-arm64" (
    call "%RECIPE_DIR%\build-arm64.bat"
    if errorlevel 1 exit /b 1
    exit /b 0
)

copy %RECIPE_DIR%\build.sh build.sh

set MSYSTEM=MINGW%ARCH%
set MSYS2_PATH_TYPE=inherit
set CHERE_INVOKING=1
bash build.sh
if errorlevel 1 exit 1
exit 0
