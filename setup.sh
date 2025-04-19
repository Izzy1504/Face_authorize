#!/bin/bash

# Check for both potential virtual env locations
if [ -d ".venv" ]; then
    VENV_DIR=".venv"
    echo "Found virtual environment at .venv"
elif [ -d "venv" ]; then
    VENV_DIR="venv"
    echo "Found virtual environment at venv"
else
    echo "Creating virtual environment..."
    python3 -m venv .venv
    VENV_DIR=".venv"
fi

# Activate the virtual environment
source $VENV_DIR/bin/activate

# Install setuptools first (which provides pkg_resources)
echo "Installing setuptools..."
pip install --upgrade pip setuptools wheel

# Install face_recognition_models first
echo "Installing face_recognition_models..."
pip install git+https://github.com/ageitgey/face_recognition_models

# Install other requirements
echo "Installing other requirements..."
pip install -r requirements.txt

# Verify installation
python -c "import pkg_resources; print('pkg_resources installed successfully!')"
python -c "import face_recognition_models; print('Face recognition models installed successfully!')"
python -c "import face_recognition; print('Face recognition library installed successfully!')"

echo "Setup complete!"
