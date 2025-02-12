# setup.sh
#!/bin/bash
echo "Creating virtual environment..."
python3 -m venv mine_venv

echo "Activating virtual environment..."
source mine_venv/bin/activate

echo "Installing requirements..."
pip install -r requirements.txt

echo "Starting Docker containers..."
docker-compose up -d

echo "Setup complete!"
echo "To activate the environment, run: source mine_venv/bin/activate"