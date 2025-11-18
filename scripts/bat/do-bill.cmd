@echo off
set ROOT=%~dp0..\..
python "%ROOT%\scripts\python\devctl_core.py" do-bill %*
