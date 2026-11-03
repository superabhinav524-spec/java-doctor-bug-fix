@echo off
setlocal
set SCRIPT_DIR=%~dp0
python -m javadoctor.cli.main %*
