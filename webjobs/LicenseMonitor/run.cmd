@ECHO OFF
:: Script to launch license monitor in the site virtual environment

:: Activate virtual environment
D:\home\site\wwwroot\env\Scripts\activate.bat

ECHO Launching license Monitor>CON
:: Start Processing Subscriptions
%WEBJOBS_PATH%\monitor.py
