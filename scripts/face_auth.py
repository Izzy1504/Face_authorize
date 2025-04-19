#!/usr/bin/env python3
import cv2
import sys
import pickle
import numpy as np
import argparse
import os
import time
import tkinter as tk
from PIL import Image, ImageTk

print("Starting face_auth.py")
print("Python path:", sys.path)

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
    print("Error importing face_recognition_models:", e)
    sys.exit(1)

# Now try to import face_recognition
try:
    import face_recognition
    print("Successfully imported face_recognition")
except ImportError as e:
    print("Error importing face_recognition:", e)
    print("\nTrying to install dependencies...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "dlib", "face_recognition", "git+https://github.com/ageitgey/face_recognition_models"])
    
    try:
        import face_recognition
        print("Successfully imported face_recognition after installation")
    except ImportError as e:
        print("Still cannot import face_recognition:", e)
        sys.exit(1)

def show_auth_ui(result, frame=None):
    root = tk.Tk()
    root.title("Face Authentication")
    root.geometry("400x450")
    root.configure(bg='white')

    canvas = tk.Canvas(root, width=400, height=450, bg='white', highlightthickness=0)
    canvas.pack()

    # Use absolute paths to the images directory
    images_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images")
    
    # Make sure the directory exists
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
    
    # Process camera frame if provided
    if frame is not None:
        # Convert the OpenCV frame to PIL format
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb_frame)
        pil_img = pil_img.resize((320, 240), Image.LANCZOS)
        cam_img_tk = ImageTk.PhotoImage(image=pil_img)
        
        # Display camera frame at the top
        canvas.create_image(200, 120, image=cam_img_tk)
    
    # Always try to use face.png for all states, with different overlays
    img_path = os.path.join(images_dir, "face.png")
    message = ""
    color = ""
    overlay_color = None
    
    if result == "success":
        message = "Authentication Successful"
        color = "green"
        overlay_color = (0, 255, 0)  # Green overlay
    elif result == "not_recognized":
        message = "Face Not Recognized"
        color = "orange"
        overlay_color = (255, 165, 0)  # Orange overlay
    else:  # failure
        message = "Authentication Failed"
        color = "red"
        overlay_color = (255, 0, 0)  # Red overlay
    
    # If face.png doesn't exist, use the fallback approach
    icon_img_tk = None
    if not os.path.exists(img_path):
        # Create a basic image with text
        img = Image.new('RGB', (100, 100), color = (255, 255, 255))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        
        if result == "success":
            draw.text((25, 40), "SUCCESS", fill=(0, 255, 0))
        elif result == "not_recognized":
            draw.text((5, 40), "NOT RECOGNIZED", fill=(255, 165, 0))
        else:
            draw.text((25, 40), "FAILURE", fill=(255, 0, 0))
            
        icon_img_tk = ImageTk.PhotoImage(img)
    else:
        # Open the face.png image
        img = Image.open(img_path)
        img = img.resize((100, 100), Image.LANCZOS)
        
        # Add colored overlay based on result
        if overlay_color:
            overlay = Image.new('RGBA', img.size, (*overlay_color, 80))  # Semi-transparent color
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            img = Image.alpha_composite(img, overlay)
            
        icon_img_tk = ImageTk.PhotoImage(img)

    # Position the status icon and text below the camera frame
    canvas.create_image(200, 320, image=icon_img_tk)
    canvas.create_text(200, 380, text=message, fill=color, font=("Arial", 14, "bold"))
    
    # Keep references to prevent garbage collection
    root.cam_img_tk = cam_img_tk if frame is not None else None
    root.icon_img_tk = icon_img_tk
    
    # Create a smooth fade-in effect
    root.attributes('-alpha', 0.0)
    
    def fade_in():
        alpha = root.attributes('-alpha')
        if alpha < 1.0:
            root.attributes('-alpha', min(alpha + 0.1, 1.0))
            root.after(50, fade_in)
            
    fade_in()
    root.after(3000, root.destroy)  # Close window after 3 seconds
    root.mainloop()

def authenticate_face(username, model_path="models/face_auth_model.pkl", confidence_threshold=0.6):
    # Kiểm tra xem model có tồn tại hay không
    if not os.path.exists(model_path):
        print("FAILURE: Model không tồn tại")
        show_auth_ui("failure")
        return False
    
    # Tải model
    try:
        with open(model_path, 'rb') as f:
            clf, face_encodings, face_names = pickle.load(f)
    except Exception as e:
        print(f"FAILURE: Không thể tải model: {e}")
        show_auth_ui("failure")
        return False
    
    # Try to handle Qt platform issues
    try:
        # Force OpenCV to use a specific backend that's available
        os.environ["QT_QPA_PLATFORM"] = "xcb"  # Try using X11 instead of Wayland
    except Exception as e:
        print(f"Warning: Could not set Qt platform: {e}")
    
    # Khởi tạo camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("FAILURE: Không thể mở camera")
        show_auth_ui("failure")
        return False
    
    # Đợi camera khởi động
    time.sleep(1)
    
    # Lấy 10 khung hình để xác thực
    max_attempts = 10
    successful_attempts = 0
    no_face_detected = 0
    last_frame = None
    
    # Create a window for smooth scanning effect - with error handling
    try:
        cv2.namedWindow('Face Authentication', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Face Authentication', 640, 480)
        window_created = True
    except Exception as e:
        print(f"Warning: Could not create window: {e}")
        window_created = False
    
    # Load face.png for overlay if possible - with robust error handling
    images_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images")
    face_overlay = None
    face_img_path = os.path.join(images_dir, "face.png")
    
    try:
        if os.path.exists(face_img_path):
            face_overlay = cv2.imread(face_img_path)
            print(f"Loaded face overlay image: {face_img_path}")
            
            # Check if image was loaded correctly
            if face_overlay is None:
                print("Warning: face.png could not be loaded properly")
            elif len(face_overlay.shape) < 3:
                print(f"Warning: Unexpected image shape: {face_overlay.shape}")
                # Convert grayscale to RGB
                face_overlay = cv2.cvtColor(face_overlay, cv2.COLOR_GRAY2BGR)
            
            # Check and convert if needed
            if face_overlay is not None:
                print(f"Face overlay shape: {face_overlay.shape}")
                # Only try to add alpha channel if shape has 3 dimensions
                if len(face_overlay.shape) == 3 and face_overlay.shape[2] == 3:
                    # Convert BGR to BGRA
                    face_overlay = cv2.cvtColor(face_overlay, cv2.COLOR_BGR2BGRA)
    except Exception as e:
        print(f"Error loading face overlay: {e}")
        face_overlay = None
    
    # Create scanning animation variables
    scan_position = 0
    scan_direction = 1
    scan_speed = 10
    
    for attempt in range(max_attempts):
        ret, frame = cap.read()
        if not ret:
            continue
            
        last_frame = frame.copy()  # Save the last frame for UI display
        display_frame = frame.copy()
        
        # Tìm khuôn mặt và mã hóa
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        
        if len(face_locations) == 0:
            no_face_detected += 1
            if window_created:
                cv2.putText(display_frame, "Looking for face...", (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 165, 0), 2)
                try:
                    cv2.imshow('Face Authentication', display_frame)
                    cv2.waitKey(1)
                except Exception as e:
                    print(f"Display error: {e}")
                    window_created = False
            continue
        
        # When a face is detected, create smooth scanning effect
        for (top, right, bottom, left) in face_locations:
            # Draw rectangle around the face
            cv2.rectangle(display_frame, (left, top), (right, bottom), (0, 255, 0), 2)
            
            # Draw scanning line effect
            if top < bottom:  # Make sure these values are valid
                if scan_position < bottom - top:
                    y_pos = top + scan_position
                    cv2.line(display_frame, (left, y_pos), (right, y_pos), (0, 255, 255), 2)
                
                # Progress indicator
                progress = min(attempt / max_attempts * 100, 100)
                cv2.rectangle(display_frame, (left, bottom + 20), 
                             (left + int((right-left) * progress/100), bottom + 30), 
                             (0, 255, 0), -1)
            
            # Overlay face template if available - with careful error handling
            if face_overlay is not None:
                try:
                    # Resize overlay to match face size
                    face_width = right - left
                    face_height = bottom - top
                    if face_width > 0 and face_height > 0:  # Valid dimensions
                        resized_overlay = cv2.resize(face_overlay, (face_width, face_height))
                        
                        # Create ROI and blend overlay
                        roi = display_frame[top:bottom, left:right]
                        # Simple alpha blending
                        alpha = 0.3  # Transparency factor
                        beta = 1.0 - alpha
                        
                        # Check if overlay has correct shape before accessing channels
                        if (len(resized_overlay.shape) == 3 and 
                            resized_overlay.shape[2] == 4 and 
                            roi.shape[0] == resized_overlay.shape[0] and 
                            roi.shape[1] == resized_overlay.shape[1]):
                            
                            # Extract alpha channel
                            overlay_alpha = resized_overlay[:, :, 3] / 255.0
                            # Process each color channel
                            for c in range(3):
                                roi[:, :, c] = (beta * roi[:, :, c] + 
                                              alpha * resized_overlay[:, :, c] * overlay_alpha)
                        elif (len(resized_overlay.shape) == 3 and 
                              resized_overlay.shape[2] == 3 and
                              roi.shape[0] == resized_overlay.shape[0] and 
                              roi.shape[1] == resized_overlay.shape[1]):
                              
                            # Simple overlay without alpha channel
                            cv2.addWeighted(roi, beta, resized_overlay, alpha, 0, roi)
                except Exception as e:
                    print(f"Overlay error: {e}")
            
        # Update scanning animation
        scan_position += scan_speed * scan_direction
        if scan_position >= (bottom - top) or scan_position <= 0:
            scan_direction *= -1
        
        # Display attempt counter and confidence info
        cv2.putText(display_frame, f"Scanning... Attempt {attempt+1}/{max_attempts}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # Show the frame with effects - with error handling
        if window_created:
            try:
                cv2.imshow('Face Authentication', display_frame)
                cv2.waitKey(1)
            except Exception as e:
                print(f"Display error: {e}")
                window_created = False
        
        # Process face encodings
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        for face_encoding in face_encodings:
            try:
                # Check if it's our custom single-user model
                if hasattr(clf, 'predict_proba') and callable(clf.predict_proba):
                    predictions = clf.predict_proba([face_encoding])[0]
                    best_match_index = np.argmax(predictions)
                    confidence = predictions[best_match_index]
                    predicted_user = clf.classes_[best_match_index]
                else:
                    # It's our custom single-user model
                    predicted_user = clf.user
                    similarity_score = clf.predict_proba([face_encoding])[0][0]
                    confidence = similarity_score
            
                # Show confidence score on frame
                conf_text = f"Confidence: {confidence:.2f}"
                cv2.putText(display_frame, conf_text, (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                
                if window_created:
                    try:
                        cv2.imshow('Face Authentication', display_frame)
                        cv2.waitKey(1)
                    except Exception as e:
                        print(f"Display error: {e}")
                        window_created = False
            
                # Kiểm tra xem người dùng dự đoán có khớp với người dùng đăng nhập không
                if predicted_user == username and confidence >= confidence_threshold:
                    successful_attempts += 1
                    print(f"Attempt {attempt+1}: Success (Confidence: {confidence:.2f})")
                    # Show green checkmark briefly
                    if window_created:
                        cv2.putText(display_frame, "✓", (right + 10, top + 20), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        try:
                            cv2.imshow('Face Authentication', display_frame)
                            cv2.waitKey(200)
                        except Exception:
                            pass
                    break
                else:
                    print(f"Attempt {attempt+1}: Wrong user or low confidence ({confidence:.2f})")
                    # Show red X briefly
                    if window_created:
                        cv2.putText(display_frame, "✗", (right + 10, top + 20), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                        try:
                            cv2.imshow('Face Authentication', display_frame)
                            cv2.waitKey(200)
                        except Exception:
                            pass
            except Exception as e:
                print(f"Attempt {attempt+1}: Error: {e}")
                continue
        
        # Smoother transition between attempts
        time.sleep(0.3)
    
    # Fade out the window if possible
    if window_created:
        try:
            for i in range(10):
                alpha = 1.0 - (i / 10.0)
                fade_frame = cv2.convertScaleAbs(last_frame, alpha=alpha, beta=0)
                cv2.imshow('Face Authentication', fade_frame)
                cv2.waitKey(30)
        except Exception:
            pass
    
    # Close any open windows
    try:
        cv2.destroyAllWindows()
    except Exception:
        pass
    
    cap.release()
    
    # Xác thực thành công nếu có ít nhất 6/10 lần thử thành công
    if successful_attempts >= 6:
        print(f"SUCCESS: {successful_attempts}/10 attempts were successful")
        show_auth_ui("success", last_frame)
        return True
    elif no_face_detected >= 7:
        print(f"FAILURE: Face not recognized in {no_face_detected}/10 attempts")
        show_auth_ui("not_recognized", last_frame)
        return False
    else:
        print(f"FAILURE: Only {successful_attempts}/10 attempts were successful")
        show_auth_ui("failure", last_frame)
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Xác thực khuôn mặt")
    parser.add_argument("--username", required=True, help="Tên người dùng để xác thực")
    parser.add_argument("--model", default="models/face_auth_model.pkl", help="Đường dẫn đến file model")
    parser.add_argument("--threshold", type=float, default=0.6, help="Ngưỡng độ tin cậy")
    args = parser.parse_args()
    
    authenticate_face(args.username, args.model, args.threshold)
