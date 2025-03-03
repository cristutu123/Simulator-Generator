@echo off
echo Installing Python 3.11...
curl -o python-3.11.0.exe https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe
python-3.11.0.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
del python-3.11.0.exe

echo Installing dependencies...
py -3.11 -m pip install -r requirements.txt

echo Building executable...
py -3.11 -m PyInstaller --onefile --windowed --name=SimulatorApp --clean --distpath=. ^
  --add-data="Source;Source" ^
  --collect-all=customtkinter ^
  Source/main.py

echo Build complete!
echo Please check the root directory for SimulatorApp.exe
pause 