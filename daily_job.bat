REM @echo off
REM Adjust the following paths as needed for your installation

REM Call the conda activation script. 
call "%USERPROFILE%\anaconda3\Scripts\activate.bat" base

REM Run your Python script. Change the path to where your script is located.
REM python -u newsroom_daily_work.py >> logfile.txt 2>&1
python newsroom_daily_work.py
REM python -u newsroom_daily_work.py 2>&1 | powershell -Command "tee -FilePath logfile.txt"

REM to push the home folder to headlinesquare-home
cd ..
robocopy "Blog" "headlinesquare-home" /E /XD ".git"
cd headlinesquare-home
git add .
git commit -m "Update home content"
git push

pause
