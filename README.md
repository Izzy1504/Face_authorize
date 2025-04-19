# Face Authentication System

This system provides secure face authentication with an iOS-style Face ID interface.

## Prerequisites

- Python 3.6 or higher
- Virtualenv
- OpenCV
- Face Recognition library
- Tkinter (for GUI)

## Installation

### Ubuntu Installation

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd face_auth_system
   ```

2. **Install system dependencies:**
   ```bash
   # Run the dependency installation script
   chmod +x install_dependencies.sh
   ./install_dependencies.sh
   ```

3. **Set up the virtual environment:**
   ```bash
   # Run the setup script to create and configure the virtual environment
   chmod +x setup.sh
   ./setup.sh
   ```

   Alternatively, you can manually set up the virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Generate UI images:**
   ```bash
   # Make the script executable
   chmod +x scripts/generate_ui_images.py
   # Run the script
   ./scripts/generate_ui_images.py
   ```

5. **Make all scripts executable:**
   ```bash
   # Make all Python scripts executable
   chmod +x scripts/*.py
   chmod +x start_face_auth.sh
   ```

## Usage

### Collect Face Data

To collect face data for a new user:
```bash
source venv/bin/activate
python scripts/collect_faces.py --username <username> --samples 30
```

### Train the Model

After collecting face data, train the model:
```bash
source venv/bin/activate
python scripts/train_model.py --data-dir data --output models/face_auth_model.pkl
```

### Authenticate a User

To authenticate a user:
```bash
source venv/bin/activate
python scripts/face_auth.py --username <username>
```

Or use the convenience script:
```bash
./start_face_auth.sh --username <username>
```

### Troubleshooting Face Recognition

To diagnose issues with face recognition:
```bash
source venv/bin/activate
python scripts/diagnose_face_recognition.py
```

## Authentication Parameters

You can customize the authentication process with these parameters:

- `--threshold <float>`: Set the confidence threshold for face recognition (default: 0.6)
- `--model <path>`: Specify a different model file (default: models/face_auth_model.pkl)

## PAM Module Integration (Advanced)

To build and install the PAM module for system authentication:
```bash
cd pam_module
make
sudo make install
```

Then configure your PAM service to use the module.

## Directory Structure

- `/data/` - Stores face images for each user
- `/models/` - Stores trained face recognition models
- `/images/` - Contains UI assets
- `/scripts/` - Python scripts for face collection, training, and authentication
- `/pam_module/` - C code for PAM integration

## Troubleshooting

If you encounter import errors related to face_recognition or dlib:
1. Make sure all system dependencies are installed via `install_dependencies.sh`
2. Try reinstalling dlib with `pip install --force-reinstall dlib`
3. Check if your Python version is compatible (Python 3.6-3.9 recommended)

For camera access issues:
1. Ensure your user has permissions to access the camera
2. Try running with sudo if needed: `sudo ./start_face_auth.sh --username <username>`
