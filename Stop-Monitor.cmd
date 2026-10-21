@echo off
if not exist "%~dp0runtime" mkdir "%~dp0runtime"
type nul > "%~dp0runtime\stop.flag"
