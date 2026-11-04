@echo off
:: Chuyen den thu muc chua file bat
pushd "%~dp0"
set PYTHON_EXE=C:\Users\Admin\AppData\Local\Python\pythoncore-3.12-64\python.exe
echo Dang cai dat thu vien bang Python 3.12...
"%PYTHON_EXE%" -m pip install -r requirements.txt
pause
popd
