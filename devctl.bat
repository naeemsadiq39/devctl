@echo off
setlocal

set ROOT=%~dp0
set PYTHONPATH=%ROOT%scripts\python

python -m devctl %*

endlocal
