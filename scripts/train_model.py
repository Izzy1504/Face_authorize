#!/usr/bin/env python3
import os
import sys
import pickle
import numpy as np
from sklearn import svm
from sklearn.neighbors import KNeighborsClassifier
import argparse

print("Starting train_model.py")
print("Python path:", sys.path)

# Try to install setuptools first if pkg_resources is missing
try:
    import pkg_resources
    print("pkg_resources is available")
except ImportError:
    print("pkg_resources is missing, installing setuptools...")
    import subprocess
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "setuptools", "wheel"])
        print("Setuptools installed successfully")
        # Force reload site packages to find the newly installed package
        import site
        import importlib
        importlib.reload(site)
    except Exception as e:
        print(f"Error installing setuptools: {e}")
        sys.exit(1)

# Try to fix model paths before importing face_recognition
try:
    import face_recognition_models
    print("Found face_recognition_models at:", face_recognition_models.__file__)
    
    # Check if model files exist
    predictor_path = face_recognition_models.pose_predictor_model_location()
    face_rec_model_path = face_recognition_models.face_recognition_model_location()
    
    print("Pose predictor exists:", os.path.exists(predictor_path))
    print("Face recognition model exists:", os.path.exists(face_rec_model_path))
    
    # Set environment variables to help dlib find the models
    os.environ["FACE_RECOGNITION_MODELS"] = os.path.dirname(os.path.dirname(face_recognition_models.__file__))
except ImportError as e:
    print(f"Error importing face_recognition_models: {e}")
    print("Trying to install face_recognition_models...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "git+https://github.com/ageitgey/face_recognition_models"])
        import face_recognition_models
        print("Successfully installed face_recognition_models")
    except Exception as e:
        print(f"Error installing face_recognition_models: {e}")
        sys.exit(1)

# Now try to import face_recognition
try:
    import face_recognition
    print("Successfully imported face_recognition")
except ImportError as e:
    print("Error importing face_recognition:", e)
    print("\nTrying to install dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "dlib", "face_recognition"])
        import face_recognition
        print("Successfully imported face_recognition after installation")
    except Exception as e:
        print(f"Error installing face_recognition: {e}")
        sys.exit(1)

def train_face_model(data_dir="data", model_output="models/face_auth_model.pkl"):
    # Kiểm tra thư mục dữ liệu
    if not os.path.exists(data_dir):
        print(f"Thư mục {data_dir} không tồn tại!")
        return
    
    # Kiểm tra thư mục đầu ra
    model_dir = os.path.dirname(model_output)
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    
    # Chuẩn bị dữ liệu
    face_encodings = []
    face_names = []
    
    # Duyệt qua các thư mục người dùng
    for user_dir in os.listdir(data_dir):
        user_path = os.path.join(data_dir, user_dir)
        if os.path.isdir(user_path):
            print(f"Đang xử lý dữ liệu cho người dùng: {user_dir}")
            
            # Duyệt qua các file ảnh trong thư mục người dùng
            for img_file in os.listdir(user_path):
                if img_file.endswith(".jpg") or img_file.endswith(".png"):
                    img_path = os.path.join(user_path, img_file)
                    
                    # Đọc ảnh và tạo mã hóa khuôn mặt
                    try:
                        image = face_recognition.load_image_file(img_path)
                        encodings = face_recognition.face_encodings(image)
                        
                        if len(encodings) > 0:
                            face_encodings.append(encodings[0])
                            face_names.append(user_dir)
                        else:
                            print(f"Không tìm thấy khuôn mặt trong ảnh: {img_path}")
                    except Exception as e:
                        print(f"Lỗi khi xử lý ảnh {img_path}: {e}")
    
    if len(face_encodings) == 0:
        print("Không có dữ liệu khuôn mặt nào được tìm thấy!")
        return
    
    # Check number of unique users
    unique_users = set(face_names)
    print(f"Số lượng người dùng phát hiện: {len(unique_users)}")
    
    # Train the model
    try:
        if len(unique_users) < 2:
            print("Cảnh báo: Chỉ phát hiện một người dùng. SVM cần ít nhất 2 lớp.")
            print("Sử dụng mô hình đặc biệt cho một người dùng...")
            
            # For a single user, we'll just store the encodings and user directly
            # We'll create a custom predict_proba function for the model
            class SingleUserModel:
                def __init__(self, encodings, user):
                    self.encodings = encodings
                    self.user = user
                    self.classes_ = np.array([user])
                
                def predict_proba(self, face_encoding):
                    # Calculate distances to all stored encodings
                    distances = np.linalg.norm(self.encodings - face_encoding, axis=1)
                    # Convert distance to similarity score (1 / (1 + distance))
                    similarities = 1 / (1 + distances)
                    # Average similarity score
                    avg_similarity = np.mean(similarities)
                    # Return as a 2D array with shape (n_samples, n_classes)
                    return np.array([[avg_similarity]])
            
            clf = SingleUserModel(np.array(face_encodings), list(unique_users)[0])
        else:
            print("Đang huấn luyện mô hình SVM...")
            clf = svm.SVC(gamma='scale', probability=True)
            clf.fit(face_encodings, face_names)
    except Exception as e:
        print(f"Lỗi khi huấn luyện mô hình SVM: {e}")
        print("Chuyển sang KNeighborsClassifier...")
        clf = KNeighborsClassifier(n_neighbors=min(3, len(face_encodings)), metric='euclidean')
        clf.fit(face_encodings, face_names)
    
    # Save model
    with open(model_output, 'wb') as f:
        pickle.dump((clf, face_encodings, face_names), f)
    
    print(f"Đã lưu mô hình vào {model_output}")
    print(f"Số lượng người dùng: {len(set(face_names))}")
    print(f"Tổng số mẫu khuôn mặt: {len(face_encodings)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Huấn luyện mô hình nhận diện khuôn mặt")
    parser.add_argument("--data-dir", default="data", help="Đường dẫn đến thư mục dữ liệu")
    parser.add_argument("--output", default="models/face_auth_model.pkl", help="Đường dẫn lưu mô hình")
    args = parser.parse_args()
    
    train_face_model(args.data_dir, args.output)

