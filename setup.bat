pip install virtualenv
virtualenv .env
call .env\Scripts\activate.bat
pip install -e common
pip show pt-common
cd client
python src\main.py