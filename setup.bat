# setup.bat
@echo off
echo Creating virtual environment...
python -m venv mine_venv

echo Activating virtual environment...
call mine_venv\Scripts\activate.bat

echo Installing requirements...
pip install -r requirements.txt

echo Starting Docker containers...
docker-compose up -d

echo Setup complete!
echo To activate the environment, run: mine_venv\Scripts\activate.bat