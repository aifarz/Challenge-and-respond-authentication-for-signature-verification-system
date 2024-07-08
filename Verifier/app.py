import os
import shutil
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tkinter import filedialog, messagebox, Button, Label, Tk
from tkinter import ttk


# Load the pre-trained model
model = load_model('best_model.h5')


def load_and_predict_image(filepath):
    # Create a temporary file path
    temp_path = 'temp_' + os.path.basename(filepath)

    # Copy the original file to the temporary file
    shutil.copy(filepath, temp_path)

    # Process the temporary file
    img = cv2.imread(temp_path, cv2.IMREAD_COLOR)
    img = cv2.resize(img, (224, 224))
    if img.shape[2] == 1:  # Convert grayscale to RGB if needed
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    img = img / 255.0
    img = img.reshape(1, 224, 224, 3)
    prediction = model.predict(img)

    # Delete the temporary file after processing
    os.remove(temp_path)

    return "Genuine" if prediction[0][0] >= 0.83 else "Forged"


def predict_images():
    filepaths = filedialog.askopenfilenames(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
    if not filepaths:
        return

    results = []
    for filepath in filepaths:
        result = load_and_predict_image(filepath)
        results.append((os.path.basename(filepath), result))

    # Display the results
    result_text = "\n".join([f"{name}: {res}" for name, res in results])
    messagebox.showinfo("Prediction Results", result_text)


# Set up the GUI
root = Tk()
root.title("Signature VerifiDcation System")
root.geometry("600x400")

# Setting up the theme
style = ttk.Style(root)
style.theme_use("alt")  # A more modern theme
style.configure("TFrame", background="#f0f0f0")
style.configure("TButton", font=('Helvetica', 12, 'bold'), borderwidth='4', background="#cccccc")
style.configure("TLabel", font=('Helvetica', 12), background="#f0f0f0")
style.map("TButton", foreground=[('pressed', '#333333'), ('active', '#ffffff')],
          background=[('pressed', '!disabled', '#666666'), ('active', '#bbbbbb')])

# Create a frame for better organization
frame = ttk.Frame(root, padding=(20, 20, 20, 20))
frame.pack(fill='both', expand=True)

# Add a label for instructions or branding
label = ttk.Label(frame, text="Please upload the signatures you want to verify:", background="#f0f0f0")
label.pack(pady=(0, 20))

# Add a button to upload images
button_load = ttk.Button(frame, text="Upload Signatures", command=predict_images)
button_load.pack(pady=10, fill='x', expand=True)

# Status label to show what's happening
status_label = ttk.Label(frame, text="", background="#f0f0f0")
status_label.pack(pady=(20, 0), fill='x')

root.mainloop()
