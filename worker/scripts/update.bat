SET PATH=%PATH%;c:\Program Files (x86)\Git\cmd
git config user.email "daniil.bilyk@eglobal-forex.com"
git config user.name "Danylo Bilyk"
git update-index --assume-unchanged config.ini
git stash
git pull
git stash pop