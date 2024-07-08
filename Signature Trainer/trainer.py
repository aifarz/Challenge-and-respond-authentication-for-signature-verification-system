import os
import numpy as np
import cv2
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping
from sklearn.model_selection import StratifiedKFold
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Function to load and preprocess images
def load_signatures(directory_path):
    signatures = []
    labels = []

    for person_folder in os.listdir(directory_path):
        person_path = os.path.join(directory_path, person_folder)
        if os.path.isdir(person_path):
            for filename in os.listdir(person_path):
                file_path = os.path.join(person_path, filename)
                image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
                if filename.startswith('original_'):
                    labels.append(0)
                elif filename.startswith('forgeries_'):
                    labels.append(1)
                else:
                    continue
                signatures.append(image)
    return signatures, labels

# Function to convert images to RGB and resize them
def to_rgb(images, target_size=(128, 128)):
    rgb_images = []
    for img in images:
        img_resized = cv2.resize(img, target_size)
        rgb_image = cv2.cvtColor(img_resized, cv2.COLOR_GRAY2RGB)
        rgb_images.append(rgb_image)
    return np.array(rgb_images)

# Simplified CNN model
def create_model():
    model = Sequential([
        Conv2D(16, (3, 3), activation='relu', input_shape=(128, 128, 3)),
        MaxPooling2D((2, 2)),
        Dropout(0.25),
        Conv2D(32, (3, 3), activation='relu'),
        MaxPooling2D((2, 2)),
        Dropout(0.25),
        Flatten(),
        Dense(64, activation='relu'),
        Dropout(0.5),
        Dense(2, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

# Function to plot training history
def plot_training_history(history, fold_no, canvas):
    fig, axs = plt.subplots(1, 2, figsize=(12, 4))
    axs[0].plot(history.history['loss'], label='Training Loss', color='red')
    axs[0].plot(history.history['val_loss'], label='Validation Loss', color='blue')
    axs[0].set_title(f'Training Progress - Fold {fold_no}')
    axs[0].set_xlabel('Epochs')
    axs[0].set_ylabel('Loss')
    axs[0].legend()

    axs[1].plot(history.history['accuracy'], label='Training Accuracy', color='green')
    axs[1].plot(history.history['val_accuracy'], label='Validation Accuracy', color='purple')
    axs[1].set_title(f'Improvement in Recognizing Images Correctly - Fold {fold_no}')
    axs[1].set_xlabel('Epochs')
    axs[1].set_ylabel('Accuracy')
    axs[1].legend()

    canvas.figure = fig
    canvas.draw()

# Function to run the training process with cross-validation
def run_training():
    status_label.config(text="Training started...")
    window.update()

    early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

    num_folds = 5
    kfold = StratifiedKFold(n_splits=num_folds, shuffle=True)

    all_images, all_labels = load_signatures(data_directory)
    all_images = to_rgb(all_images)
    all_images = all_images / 255.0  # Normalize images
    all_labels = np.array(all_labels)

    fold_no = 1
    for train_idx, val_idx in kfold.split(all_images, all_labels):
        print(f'Training fold {fold_no}...')
        model = create_model()

        datagen = ImageDataGenerator(
            rotation_range=5,
            width_shift_range=0.05,
            height_shift_range=0.05,
            shear_range=0.05,
            zoom_range=0.05,
            horizontal_flip=True,
            fill_mode='nearest'
        )

        train_gen = datagen.flow(all_images[train_idx], all_labels[train_idx], batch_size=32)

        history = model.fit(
            train_gen,
            epochs=5,
            validation_data=(all_images[val_idx], all_labels[val_idx]),
            callbacks=[early_stopping]
        )

        model.save(f'best_model_fold_{fold_no}.h5')
        plot_training_history(history, fold_no, canvas)
        fold_no += 1

    status_label.config(text="Training completed.")
    messagebox.showinfo("Info", "Training completed successfully!")

# Setup the main window using Tkinter
window = tk.Tk()
window.title("CNN Training UI")

# UI elements configuration
start_button = tk.Button(window, text="Start Training", command=run_training)
status_label = tk.Label(window, text="Status: Ready")
fig = plt.figure(figsize=(12, 4))
canvas = FigureCanvasTkAgg(fig, master=window)

# Layout the UI elements
start_button.pack(pady=10)
status_label.pack(pady=10)
canvas.get_tk_widget().pack()

# Define directories
current_working_directory = os.getcwd()
data_directory = os.path.join(current_working_directory, 'Data')

# Start the main Tkinter loop
window.mainloop()
