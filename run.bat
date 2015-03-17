@echo off
chdir /d "C:\Program Files\Checkers-Over-IP"
git fetch
set COUNT=
for /f "delims=" %%a in ('git rev-list HEAD...origin/master --count') do @set COUNT=%%a
ECHO %COUNT%
timeout /T 3
if '%COUNT%' == '' (goto runWithoutPull) else (goto runWithPull)

:runWithPull
:::::::::::::::::::::::::::::::::::::::::
:: Automatically check & get admin rights
:::::::::::::::::::::::::::::::::::::::::
CLS
ECHO.
ECHO =============================
ECHO There are updates for your checkers game.:) Click yes to update.
ECHO =============================

ECHO.
ECHO =============================
ECHO Running Admin shell
ECHO =============================

:checkPrivileges
NET FILE 1>NUL 2>NUL
if '%errorlevel%' == '0' ( goto gotPrivileges ) else ( goto getPrivileges )

:getPrivileges
if '%1'=='ELEV' (shift & goto gotPrivileges)
ECHO.
ECHO **************************************
ECHO Invoking UAC for Privilege Escalation
ECHO **************************************

setlocal DisableDelayedExpansion
set "batchPath=%~0"
setlocal EnableDelayedExpansion
ECHO Set UAC = CreateObject^("Shell.Application"^) > "%temp%\OEgetPrivileges.vbs"
ECHO UAC.ShellExecute "!batchPath!", "ELEV", "", "runas", 1 >> "%temp%\OEgetPrivileges.vbs"
"%temp%\OEgetPrivileges.vbs"
exit /B

:gotPrivileges
::::::::::::::::::::::::::::
::START
::::::::::::::::::::::::::::
setlocal & pushd .
git pull

:runWithoutPull
start pythonw main.py