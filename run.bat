:@echo off
chdir /d "C:\Program Files\Checkers-Over-IP"
ECHO Updating local repo....
git fetch
ECHO Checking for differences....
set COUNT=
for /f "delims=" %%a in ('git diff --numstat HEAD origin/master') do @set COUNT=%%a
set _count_=%COUNT:~0,1%
ECHO %COUNT%
ECHO %_count_%
if '%_count_%' == '' (echo No need to pull) else (echo Update needed)
TIMEOUT /T 15
if '%_count_%' == '' (goto runWithoutPull) else (goto runWithPull)


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