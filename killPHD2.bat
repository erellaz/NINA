@ECHO off
CLS


REM Kill PHD2 if running to ensure we can access log files for backup
ECHO +++ KILL PHD2 IF RUNNING
c:\Windows\system32\taskkill.exe  /F /IM phd2.exe


:EXIT