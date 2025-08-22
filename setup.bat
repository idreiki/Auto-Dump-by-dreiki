@echo off
echo Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller

echo Installing pylingual from source...
cd pylingual-main
pip install poetry>=2.0
poetry install
cd ..

echo Building executable...
python build.py

echo Setup complete!
pause
