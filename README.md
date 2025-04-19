# Face Authentication System

This system provides secure face authentication with an iOS-style Face ID interface.

## Prerequisites

- Python 3.6 or higher
- Virtualenv
- OpenCV
- Face Recognition library
- Tkinter (for GUI)

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd face_auth_system
   ```

2. **Set up the virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install the required packages:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Make the scripts executable:**
   ```bash
   ./make_executable.sh
   ```

## Usage

### Register a Face

To register a new face for a user:
```bash
./face_auth.sh --train --user <username>
```

### Authenticate a User

To authenticate a user:
```bash
./face_auth.sh --user <username>
```

### List Registered Users

To list all registered users:
```bash
./face_auth.sh --list
```

## Authentication Parameters

You can customize the authentication process with these parameters:

- `--attempts <number>`: Set the maximum number of recognition attempts (default: 10)
- `--required <number>`: Set the minimum number of successful recognitions required (default: 6)
- `--threshold <float>`: Set the confidence threshold for face recognition (default: 0.6)

## Troubleshooting

If you encounter import errors, the system will try to automatically create a symlink from `train_model.py` to `face_train.py`. You can manually create this with:

```bash
# On Linux/macOS
ln -s train_model.py face_train.py

# On Windows
copy train_model.py face_train.py
```

## Directory Structure

- `/data/` - Stores face images for each user
- `/models/` - Stores trained face recognition models
- `/images/` - Contains UI assets

## Additional Information

For more details on each script and its functionality, refer to the `scripts/README.md` file.
