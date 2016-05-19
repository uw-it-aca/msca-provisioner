@ECHO OFF
:: Script to launch license manager in the site virtual environment

:: Activate virtual environment
D:\home\site\wwwroot\env\Scripts\activate.bat

ECHO Launching License Manager>CON
:: Start Processing Subscriptions
%WEBJOBS_PATH%\manage.py
