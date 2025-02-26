import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image

# Load the trained model
model = load_model("./model/fingerprint_model.h5")

# Ensure this order matches `train_model.py` detected order
blood_groups = ['AB_neg', 'AB_pos', 'A_neg', 'A_pos', 'B_neg', 'B_pos', 'O_neg', 'O_pos']

# Load test fingerprint image
test_image = image.load_img(r"processed_fingerprint_dataset/O_neg/cluster_7_653.jpg", target_size=(128, 128))
test_image = image.img_to_array(test_image) / 255.0
test_image = np.expand_dims(test_image, axis=0)

# Make prediction
prediction = model.predict(test_image)
predicted_class = np.argmax(prediction)

# Print correct blood group
print(f"Predicted Blood Group: {blood_groups[predicted_class]}")

