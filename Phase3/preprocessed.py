import os
import cv2

def preprocess_image(image_path, max_size_kb=100):
    img = cv2.imread(image_path)
    if img is None:
        return
    
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    processed_img = cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGR)

    #jpeg compression
    quality = 90
    while quality > 10:
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        _, encoded_img = cv2.imencode('.jpg', processed_img, encode_param)
        if (len(encoded_img) / 1024.0) <= max_size_kb:
            break
        quality -= 5

    with open(image_path, 'wb') as f:
        f.write(encoded_img)

def run_preprocessing():
    for folder in ["train/images", "val/images", "test/images"]:
        dir_path = os.path.join("dataset", folder)
        if not os.path.exists(dir_path):
            continue
        
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    preprocess_image(os.path.join(root, file))

if __name__ == "__main__":
    run_preprocessing()