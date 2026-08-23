import os
import cv2
import numpy as np

def convert_dataset_to_grayscale(dataset_dir="dataset"):
    print("[1/3] Starting dataset grayscale conversion and compression...")
    processed_count = 0

    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 10]

    for split in ["train", "valid", "test"]:
        img_folder = os.path.join(dataset_dir, split, "images")
        if not os.path.exists(img_folder):
            continue
            
        for root, _, files in os.walk(img_folder):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    file_path = os.path.join(root, file)
                    img = cv2.imread(file_path)
                    if img is None:
                        continue
                    
                    # Grayscale
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                    processed_img = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
                    
                    # JPEG Compression 
                    _, compressed_bytes = cv2.imencode('.jpeg', processed_img, encode_param)
                    with open(file_path, 'wb') as f:
                        f.write(compressed_bytes.tobytes())
                        
                    processed_count += 1

    print(f"Converted and compressed {processed_count} images successfully.\n")

if __name__ == "__main__":
    convert_dataset_to_grayscale()