import os 
import cv2
import numpy as np

def apply_offline_augmentations(dataset_dir = "dataset"):
    print("[2/3] Starting offline data augmentations...")
    train_img_folder = os.path.join(dataset_dir, "train", "images")
    train_label_folder = os.path.join(dataset_dir, "train", "labels")

    if not os.path.exists(train_img_folder):
        return
    
    augmented_count = 0 
    for file in os.listdir(train_img_folder):
        if file.lower().endswith(('.jpeg','.jpg','.png')) and not ("_bright" in file or "_noise" in file):
            img_path = os.path.join(train_img_folder, file)
            base_name = os.path.splittext(file)[0]
            label_path = os.path.join(train_label_folder, f"{base_name}.txt")

            img=cv2.imread(img_path)
            if img is None:
                continue

            bright_img = cv2.convertScaleAbs(img, alpha=1.2, beta=15)
            cv2.imwrite(os.path.join(train_img_folder, f"{base_name}_bright.jpg"), bright_img)

            noise = np.random.normal(0,10,img.shape).astype(np.uint8)
            noisy_img = cv2.add(img, noise)
            cv2.imwrite(os.path.join(train_img_folder, f"{base_name}_noise.jpg"), noisy_img)

            if os.path.exists(label_path):
                with open(label_path, 'r') as f:
                    label_content = f.read()
                with open(os.path.join(train_label_folder, f"{base_name}_bright.txt"), 'w') as f:
                    f.write(label_content)
                with open(os.path.join(train_label_folder, f"{base_name}_noise.txt"), 'w') as f:
                    f.write(label_content)

            augmented_count += 2
    
    print(f"Generated {augmented_count} augmented training samples with labels. \n")

if __name__ == "__main__":
    apply_offline_augmentations()