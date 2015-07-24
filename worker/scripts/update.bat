SET PATH=%PATH%;c:\Program Files (x86)\Git\cmd
git status | find "modified"
set MODIFIED=%errorlevel%
if %MODIFIED% EQ 0:
    git stash
git pull
if %MODIFIED% EQ 0:
    git stash pop