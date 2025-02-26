import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# Define dataset path
dataset_path = "processed_fingerprint_dataset"

# Data Augmentation
datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=20,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    validation_split=0.2
)

train_data = datagen.flow_from_directory(dataset_path, target_size=(128, 128),
                                         batch_size=32, class_mode='categorical', subset="training")

val_data = datagen.flow_from_directory(dataset_path, target_size=(128, 128),
                                       batch_size=32, class_mode='categorical', subset="validation")

# Define CNN model
model = Sequential([
    Conv2D(32, (3,3), activation='relu', input_shape=(128, 128, 3)),
    MaxPooling2D(pool_size=(2,2)),
    Conv2D(64, (3,3), activation='relu'),
    MaxPooling2D(pool_size=(2,2)),
    Flatten(),
    Dense(128, activation='relu'),
    Dropout(0.5),  # Prevent overfitting
    Dense(8, activation='softmax')  # 8 blood groups
])

# Compile and train the model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.fit(train_data, validation_data=val_data, epochs=30)  # Increase epochs for better accuracy

# Save the trained model
model.save("blood_group_model.h5")
print("Model Training Completed and Saved as 'blood_group_model.h5'")
