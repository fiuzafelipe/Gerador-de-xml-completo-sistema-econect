@echo off
title Fiuza Tecnology - Build Executavel
mode con: cols=90 lines=35
color 0B

cd /d "%~dp0"

echo.
echo ==========================================================
echo                 FIUZA TECNOLOGY BUILD
echo ==========================================================
echo.

:: ==========================================================
:: PYTHON
:: ==========================================================

set PYTHON=py -3.12

:: ==========================================================
:: LIMPEZA
:: ==========================================================

echo Limpando builds antigos...
echo.

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

for /d /r %%d in (__pycache__) do (
    if exist "%%d" rmdir /s /q "%%d"
)

if exist Gerador_XML.spec del /f /q Gerador_XML.spec
if exist updater.spec del /f /q updater.spec

echo Limpeza concluida.
echo.

:: ==========================================================
:: BUILD GERADOR_XML
:: ==========================================================

echo ==========================================================
echo           GERANDO GERADOR_XML.EXE
echo ==========================================================
echo.

%PYTHON% -m PyInstaller ^
--noconfirm ^
--clean ^
--windowed ^
--paths=. ^
--collect-all customtkinter ^
--collect-all pymysql ^
--collect-all requests ^
--collect-all certifi ^
--hidden-import=ui ^
--hidden-import=ui.login ^
--hidden-import=ui.dashboard ^
--hidden-import=core ^
--hidden-import=core.database ^
--hidden-import=core.logs ^
--hidden-import=core.auth ^
--hidden-import=updater ^
--add-data "assets;assets" ^
--icon=assets/icon.ico ^
--name Gerador_XML ^
main.py

if errorlevel 1 (
    echo.
    echo ERRO AO GERAR GERADOR_XML.EXE
    pause
    exit /b
)

:: ==========================================================
:: BUILD UPDATER
:: ==========================================================

echo.
echo ==========================================================
echo              GERANDO UPDATER.EXE
echo ==========================================================
echo.

if exist updater_launcher.py (

    %PYTHON% -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --onefile ^
    --windowed ^
    --collect-all requests ^
    --collect-all certifi ^
    --hidden-import=updater ^
    --hidden-import=core.logs ^
    --icon=assets/icon.ico ^
    --name updater ^
    updater_launcher.py

) else (

    echo.
    echo ERRO:
    echo updater_launcher.py nao encontrado.
    echo.
)

:: ==========================================================
:: COPIA UPDATER
:: ==========================================================

echo.
echo Copiando updater...

if exist dist\updater.exe (

    copy /Y ^
    dist\updater.exe ^
    dist\Gerador_XML\updater.exe >nul

    echo updater.exe copiado com sucesso.

) else (

    echo.
    echo AVISO:
    echo updater.exe nao foi gerado.
    echo.

)

:: ==========================================================
:: RESULTADO
:: ==========================================================

echo.
echo ==========================================================
echo                 BUILD FINALIZADA
echo ==========================================================
echo.

if exist dist\Gerador_XML\Gerador_XML.exe (

    echo.
    echo BUILD GERADA COM SUCESSO!
    echo.
    echo Estrutura:
    echo.
    echo dist\Gerador_XML\
    echo    Gerador_XML.exe

    if exist dist\Gerador_XML\updater.exe (
        echo    updater.exe
    )

    echo    assets\
    echo    _internal\
    echo.

    explorer dist\Gerador_XML

    echo msgbox "Build gerada com sucesso!",64,"Fiuza Tecnology" > popup.vbs
    start /wait popup.vbs
    del popup.vbs

) else (

    echo.
    echo ERRO AO GERAR EXECUTAVEL!
    echo.

)

echo.
pause