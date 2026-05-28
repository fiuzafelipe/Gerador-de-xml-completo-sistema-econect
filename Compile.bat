@echo off

title Fiuza Tecnology - Build Executavel
mode con: cols=90 lines=32
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
:: LIMPA BUILDS ANTIGOS
:: ==========================================================

echo Limpando builds antigos...

if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist __pycache__ rmdir /s /q __pycache__

for /d /r %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"

if exist Gerador_XML.spec del /f /q Gerador_XML.spec

echo.
echo Build limpo com sucesso.
echo.

:: ==========================================================
:: GERANDO EXECUTAVEL
:: ==========================================================

echo ==========================================================
echo              GERANDO EXECUTAVEL
echo ==========================================================
echo.

%PYTHON% -m PyInstaller ^
--noconfirm ^
--clean ^
--windowed ^
--paths=. ^
--collect-all customtkinter ^
--collect-all pymysql ^
--hidden-import=ui ^
--hidden-import=ui.login ^
--hidden-import=ui.dashboard ^
--hidden-import=core ^
--hidden-import=core.database ^
--hidden-import=core.logs ^
--hidden-import=core.auth ^
--hidden-import=core.update_checker ^
--hidden-import=updater ^
--add-data "assets;assets" ^
--icon=assets/icon.ico ^
--name Gerador_XML ^
main.py

:: ==========================================================
:: VERIFICA RESULTADO
:: ==========================================================

echo.
echo ==========================================================
echo                 BUILD FINALIZADA
echo ==========================================================
echo.

if exist dist\Gerador_XML\Gerador_XML.exe (

    echo EXECUTAVEL GERADO COM SUCESSO!
    echo.
    echo Caminho:
    echo dist\Gerador_XML\
    echo.

    explorer dist\Gerador_XML

    echo msgbox "Executavel gerado com sucesso!", 64, "Fiuza Tecnology" > popup.vbs
    start /wait popup.vbs
    del popup.vbs

) else (

    echo ERRO AO GERAR EXECUTAVEL!
)

echo.
pause