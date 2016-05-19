@ECHO OFF
:: Script to launch event loader in the site virtual environment

:: Activate virtual environment
D:\home\site\wwwroot\env\Scripts\activate.bat

ECHO Launching Event Loader>CON
:: Start Processing Subscriptions
%WEBJOBS_PATH%\load.py
