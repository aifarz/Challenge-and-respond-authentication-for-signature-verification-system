import os
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess  # Import subprocess module

class SignatureTrainerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Offline Signature Verification - Trainer")
        self.master.geometry("400x200")  # Set the application size
        self.master.config(bg='white')  # Background color for the main window

        # Initialize variables
        self.base_dir = "C:\\Users\\farza\\Offline Signature Verification\\Signature Trainer\\Data"
        self.max_signatures = 24  # Max signatures per type

        # Main window buttons
        self.data_button = tk.Button(self.master, text="Data", command=self.open_data_window, bg='#f0f0f0', width=20)
        self.data_button.pack(pady=10)

        self.trainer_button = tk.Button(self.master, text="Trainer", command=self.run_trainer, bg='#f0f0f0', width=20)
        self.trainer_button.pack(pady=10)

        self.check_signature_button = tk.Button(self.master, text="Check Signature Data", command=self.check_signatures, bg='#f0f0f0', width=20)
        self.check_signature_button.pack(pady=10)

    def run_trainer(self):
        # This method uses subprocess to run the trainer.py script
        subprocess.Popen(["python", "trainer.py"])



    def open_data_window(self):
        self.master.withdraw()
        self.data_window = tk.Toplevel()
        self.data_window.title("Manage Data")
        self.data_window.geometry("400x200")
        self.data_window.protocol("WM_DELETE_WINDOW", self.on_close_data_window)

        add_original_button = tk.Button(self.data_window, text="Add Original Signature", command=lambda: self.add_signature('original'), bg='#f0f0f0')
        add_original_button.pack(pady=10)

        add_forgery_button = tk.Button(self.data_window, text="Add Forged Signature", command=lambda: self.add_signature('forgeries'), bg='#f0f0f0')
        add_forgery_button.pack(pady=10)

        confirm_button = tk.Button(self.data_window, text="Confirm Signatures", command=self.confirm_signatures, bg='#f0f0f0')
        confirm_button.pack(pady=20)

    def add_signature(self, type):
        file_paths = filedialog.askopenfilenames(filetypes=[("PNG files", "*.png")])
        if not file_paths:
            return

        for file_path in file_paths:
            new_dir = os.path.join(self.base_dir, type)
            os.makedirs(new_dir, exist_ok=True)
            new_file_name = os.path.basename(file_path)
            new_file_path = os.path.join(new_dir, new_file_name)
            os.rename(file_path, new_file_path)
        messagebox.showinfo("Success", f"{len(file_paths)} {type} signatures added.")

    def confirm_signatures(self):
        messagebox.showinfo("Confirm", "Signatures confirmed and processed.")

    def check_signatures(self):
        signatures, labels = self.load_signatures(self.base_dir)
        genuine_count = labels.count(0)
        forged_count = labels.count(1)
        messagebox.showinfo("Signature Data Check", f"Total signatures: {len(signatures)}\nGenuine: {genuine_count}, Forged: {forged_count}")

    def load_signatures(self, directory_path):
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

    def on_close_data_window(self):
        self.data_window.destroy()
        self.master.deiconify()

if __name__ == "__main__":
    root = tk.Tk()
    app = SignatureTrainerApp(root)
    root.mainloop()
