@echo off
title Fiuza Technology - Build Executavel
mode con: cols=90 lines=35
color 0B

cd /d "%~dp0"

echo.
echo ==========================================================
echo                 FIUZA TECHNOLOGY BUILD
echo ==========================================================
echo.

set PYTHON=py -3.12

echo Limpando builds antigos e processos presos...
echo.

taskkill /f /im Gerador_XML.exe >nul 2>&1
taskkill /f /im updater.exe >nul 2>&1
taskkill /f /im pyinstaller.exe >nul 2>&1

if exist build rmdir /s /q build
if exist build_updater rmdir /s /q build_updater
if exist dist rmdir /s /q dist
if exist dist_updater rmdir /s /q dist_updater

if exist Gerador_XML.spec del /f /q Gerador_XML.spec
if exist updater.spec del /f /q updater.spec

for /d /r %%d in (__pycache__) do (
    if exist "%%d" rmdir /s /q "%%d"
)

echo Limpeza concluida.
echo.

:: ==========================================================
:: BUILD GERADOR_XML
:: ==========================================================
echo ==========================================================
echo               GERANDO GERADOR_XML.EXE
echo ==========================================================
echo.

%PYTHON% -m PyInstaller ^
--noconfirm ^
--clean ^
--onedir ^
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
--hidden-import=core.update_checker ^
--add-data "assets;assets" ^
--icon=assets/icon.ico ^
--name Gerador_XML ^
main.py

if errorlevel 1 (
    echo.
    echo ERRO AO GERAR GERADOR_XML.EXE
    goto FALHA_FINAL
)

timeout /t 2 >nul

:: ==========================================================
:: BUILD UPDATER (SANDBOX ISOLADO)
:: ==========================================================
echo.
echo ==========================================================
echo               GERANDO UPDATER.EXE
echo ==========================================================
echo.

if exist updater_launcher.py (

    %PYTHON% -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --onefile ^
    --windowed ^
    --uac-admin ^
    --specpath="." ^
    --workpath="build_updater" ^
    --distpath="dist_updater" ^
    --collect-all requests ^
    --collect-all certifi ^
    --hidden-import=updater ^
    --hidden-import=core.logs ^
    --icon=assets/icon.ico ^
    --name updater ^
    updater_launcher.py

) else (
    echo.
    echo ERRO: updater_launcher.py nao encontrado.
    goto FALHA_FINAL
)

if errorlevel 1 (
    echo.
    echo ERRO AO GERAR UPDATER.EXE
    goto FALHA_FINAL
)

:: Limpeza de pastas temporárias de código, mantendo apenas os executáveis finais
if exist build rmdir /s /q build >nul 2>&1
if exist build_updater rmdir /s /q build_updater >nul 2>&1
if exist updater.spec del /f /q updater.spec >nul 2>&1

:: ==========================================================
:: RESULTADO FINAL
:: ==========================================================
echo.
echo ==========================================================
echo                  BUILD FINALIZADA
echo ==========================================================
echo.
echo COMPILACAO CONCLUIDA COM SUCESSO!
echo.
echo Como o Windows bloqueia copias automatizadas nesta pasta,
echo faça a uniao manual para o seu instalador:
echo.
echo 1. Abra a pasta 'dist_updater', copie o 'updater.exe'.
echo 2. Cole ele dentro de 'dist\Gerador_XML\'.
echo.

:: Abre as duas pastas na tela para facilitar o seu clique e arrastar
explorer dist
explorer dist_updater

echo msgbox "Compilacao concluida! Junte os arquivos manualmente.",64,"Fiuza Technology" > popup.vbs
start /wait popup.vbs
del popup.vbs
goto FIM

:FALHA_FINAL
echo.
echo ATENCAO: O PROCESSO DE BUILD FALHOU!
echo.

:FIM
echo Pressione qualquer tecla para fechar esta janela...
pause >nul