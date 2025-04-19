#!/usr/bin/env python3
import os
import sys
import importlib
import site

print("Python version:", sys.version)
print("Python executable:", sys.executable)
print("Python path:", sys.path)

# Check if face_recognition is installed
try:
    import face_recognition
    print("\nFace Recognition version:", face_recognition.__version__ if hasattr(face_recognition, "__version__") else "Unknown")
    print("Face Recognition path:", face_recognition.__file__)
except ImportError as e:
    print("Error importing face_recognition:", e)

# Check if face_recognition_models is installed
try:
    import face_recognition_models
    print("\nFace Recognition Models path:", face_recognition_models.__file__)
    
    # Check model files
    predictor_path = face_recognition_models.pose_predictor_model_location()
    face_rec_model_path = face_recognition_models.face_recognition_model_location()
    
    print("Pose predictor exists:", os.path.exists(predictor_path))
    print("Pose predictor path:", predictor_path)
    print("Face recognition model exists:", os.path.exists(face_rec_model_path))
    print("Face recognition model path:", face_rec_model_path)
except ImportError as e:
    print("Error importing face_recognition_models:", e)

# Check dlib installation
try:
    import dlib
    print("\nDlib version:", dlib.__version__ if hasattr(dlib, "__version__") else "Unknown")
    print("Dlib path:", dlib.__file__)
except ImportError as e:
    print("Error importing dlib:", e)

print("\nSite packages directories:")
for path in site.getsitepackages():
    print(f"- {path}")
