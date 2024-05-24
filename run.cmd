@echo off
rem
cd /d "%~dp0"
if not defined _OLD_VIRTUAL_PROMPT (
	call env\Scripts\activate
)
flask --debug -A app run -h 0.0.0.0 -p 80
