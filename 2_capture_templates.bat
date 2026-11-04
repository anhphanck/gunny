@echo off
pushd "%~dp0"
set PYTHON_EXE=C:\Users\Admin\AppData\Local\Python\pythoncore-3.12-64\python.exe
echo Dang khoi chay cong cu chup anh mau...
"%PYTHON_EXE%" capture_templates.py
pause
popd
