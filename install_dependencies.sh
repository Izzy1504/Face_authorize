#!/bin/bash

echo "Installing system dependencies for dlib and face_recognition..."

# Install system dependencies for building dlib
sudo apt-get update
sudo apt-get install -y build-essential cmake libopenblas-dev liblapack-dev libx11-dev libgtk-3-dev

# Activate the virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Install Python dependencies
pip install --upgrade pip
pip install --upgrade setuptools wheel  # This provides pkg_resources
pip install numpy scipy
pip install dlib --no-cache-dir
pip install face_recognition_models --no-cache-dir
pip install git+https://github.com/ageitgey/face_recognition_models --no-cache-dir
pip install face_recognition --no-cache-dir
pip install -r requirements.txt

# Test the installation
echo "Testing the installation..."
python -c "import pkg_resources; print('pkg_resources installed successfully!')"
python -c "import face_recognition_models; print('Face recognition models location:', face_recognition_models.__file__)"
python -c "import face_recognition; print('Face recognition location:', face_recognition.__file__)"

echo "Installation complete!"
