import cv2
import os

dataset_path = "processed_fingerprint_dataset"

for blood_group in os.listdir(dataset_path):
    blood_group_path = os.path.join(dataset_path, blood_group)
    
    for img_name in os.listdir(blood_group_path):
        img_path = os.path.join(blood_group_path, img_name)
        
        if not img_name.endswith((".jpg", ".png")):
            print(f"Converting {img_path} to JPG...")
            img = cv2.imread(img_path)
            new_path = img_path.rsplit(".", 1)[0] + ".jpg"
            cv2.imwrite(new_path, img)
            os.remove(img_path)  # Remove the old file
