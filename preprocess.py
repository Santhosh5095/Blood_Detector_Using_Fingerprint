import cv2
import os

input_folder = "fingerprint_dataset"
output_folder = "processed_fingerprint_dataset"
os.makedirs(output_folder, exist_ok=True)

for blood_group in os.listdir(input_folder):
    os.makedirs(os.path.join(output_folder, blood_group), exist_ok=True)
    for img_name in os.listdir(os.path.join(input_folder, blood_group)):
        img_path = os.path.join(input_folder, blood_group, img_name)
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)  # Convert to grayscale
        img = cv2.resize(img, (128, 128))  # Resize to 128x128
        img = cv2.GaussianBlur(img, (5, 5), 0)  # Reduce noise
        img = img / 255.0  # Normalize pixel values

        # Save processed image
        save_path = os.path.join(output_folder, blood_group, img_name)
        cv2.imwrite(save_path, img * 255)

print("Preprocessing Completed! Check 'processed_fingerprint_dataset' folder.")
