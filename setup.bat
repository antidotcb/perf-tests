pip install virtualenv
virtualenv .env
call .env\Scripts\activate.bat
pip install -e common
pip show pt-common

SET PATH=%PATH%;c:\Program Files (x86)\Git\cmd
git config core.autocrlf true
git config user.email "daniil.bilyk@eglobal-forex.com"
git config user.name "Danylo Bilyk"
git update-index --no-assume-unchanged config.ini