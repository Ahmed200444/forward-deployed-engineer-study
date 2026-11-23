@echo off
rem Double-click to start FDE Study. It opens in your browser at http://localhost:8765/
rem Keep the black window open while you study; close it to stop.
title FDE Study
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0serve.ps1"
if errorlevel 1 pause
