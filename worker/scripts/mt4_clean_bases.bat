del /Q /F C:\MetaTrader4Server\bases\orders.dat
del /Q /F C:\MetaTrader4Server\bases\users.dat
del /Q /F C:\MetaTrader4Server\config\managers.ini
copy /Y C:\MetaTrader4Server\bases\users.dat.original C:\MetaTrader4Server\bases\users.dat
copy /Y C:\MetaTrader4Server\config\managers.ini.original C:\MetaTrader4Server\config\managers.ini.original