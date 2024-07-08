import tkinter as tk  # Import the tkinter module for GUI
from tkinter import messagebox, filedialog  # Import messagebox and filedialog for user interactions
from cryptography.hazmat.primitives import serialization, hashes  # Import cryptographic primitives
from cryptography.hazmat.primitives.asymmetric import padding  # Import padding for asymmetric encryption
from cryptography.hazmat.primitives.serialization import load_pem_private_key  # Import function to load private key
from cryptography.x509 import load_pem_x509_certificate  # Import function to load x509 certificate
import secrets  # Import secrets module for generating secure random numbers
import base64  # Import base64 module for encoding/decoding
import logging  # Import logging module for logging events
import time  # Import time module for handling timeouts
import subprocess  # Import subprocess module to run the data.py file

# Configure logging
logging.basicConfig(filename='login_system.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Secure Login System")  # Set the title of the window
        self.geometry("500x400")  # Set the window size
        self.configure(bg="#e0e0e0")  # Set the background color to light grey
        self.user_certificates = {
            "Admin 1": r"C:\Users\farza\Certificate Authority\admin1_certificate.pem",
            "Admin 2": r"C:\Users\farza\Certificate Authority\admin2_certificate.pem"
        }  # Dictionary of user certificates
        self.challenge = None  # Initialize the challenge variable
        self.challenge_time = None  # Initialize the challenge time variable
        self.challenge_id = None  # Initialize the challenge ID variable
        self.failed_attempts = 0  # Initialize the failed attempts counter
        self.lockout_duration = 0  # Initialize the lockout duration
        self.login_window = None  # Initialize the login window variable
        self.user_choice = tk.StringVar(self)  # Create a StringVar for user selection
        self.user_choice.set("Admin 1")  # Set the default value
        self.create_widgets()  # Call the method to create UI widgets

    def create_widgets(self):
        # Create a main frame
        main_frame = tk.Frame(self, bg="#e0e0e0", padx=20, pady=20)
        main_frame.pack(expand=True)

        # Add a title label
        tk.Label(main_frame, text="Welcome to the Secure Login System", bg="#e0e0e0", font=("Arial", 16, "bold")).pack(pady=10)

        # Create a frame for user selection
        user_frame = tk.Frame(main_frame, bg="#e0e0e0", padx=10, pady=10, bd=1, relief="solid")
        user_frame.pack(pady=20)

        tk.Label(user_frame, text="Select User:", bg="#e0e0e0", font=("Arial", 12)).pack(pady=10)

        # Create radio buttons for user selection
        tk.Radiobutton(user_frame, text="Admin 1", variable=self.user_choice, value="Admin 1", bg="#e0e0e0", font=("Arial", 12)).pack(pady=5)
        tk.Radiobutton(user_frame, text="Admin 2", variable=self.user_choice, value="Admin 2", bg="#e0e0e0", font=("Arial", 12)).pack(pady=5)

        # Create a frame for the login button
        button_frame = tk.Frame(main_frame, bg="#e0e0e0", padx=10, pady=10)
        button_frame.pack(pady=20)

        login_button = tk.Button(button_frame, text="Login", command=self.login, bg="#808080", fg="white", font=("Arial", 12, "bold"), padx=20, pady=10)  # Create a login button
        login_button.pack()
        logging.info("Application started and UI initialized.")  # Log the initialization

    def login(self):
        user = self.user_choice.get()  # Get the selected user
        cert_path = self.user_certificates[user]  # Get the certificate path for the selected user
        with open(cert_path, 'rb') as cert_file:
            cert = load_pem_x509_certificate(cert_file.read())  # Load the user's certificate
            public_key = cert.public_key()  # Get the public key from the certificate
        self.challenge = secrets.token_bytes(32)  # Generate a secure random challenge
        self.challenge_time = time.time()  # Record the time when the challenge was generated
        self.challenge_id = secrets.token_hex(16)  # Generate a unique challenge ID
        print(f"Original Challenge for {user}: {base64.b64encode(self.challenge).decode()}")  # Print the original challenge
        encrypted_challenge = public_key.encrypt(
            self.challenge,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),  # Use MGF1 with SHA256
                algorithm=hashes.SHA256(),  # Use SHA256 for the padding algorithm
                label=None
            )
        )  # Encrypt the challenge with the public key
        logging.info(f"User '{user}' initiated login, challenge encrypted.")  # Log the encryption
        print(f"Encrypted Challenge for {user}: {base64.b64encode(encrypted_challenge).decode()}")  # Print the encrypted challenge

        # Close any existing login window
        if self.login_window is not None and tk.Toplevel.winfo_exists(self.login_window):
            self.login_window.destroy()

        self.show_login_screen(base64.b64encode(encrypted_challenge).decode(), self.challenge_id)  # Show the login screen with the encrypted challenge

    def show_login_screen(self, challenge, challenge_id):
        self.login_window = tk.Toplevel(self)  # Create a new window for the login screen
        self.login_window.geometry("400x200")  # Set the window size
        self.login_window.configure(bg="#e0e0e0")  # Set the background color to light grey

        # Add a title and instructions
        tk.Label(self.login_window, text="Key File Authentication", bg="#e0e0e0", font=("Arial", 14, "bold")).pack(pady=10)
        tk.Label(self.login_window, text="Please select your private key file to decrypt the challenge.", bg="#e0e0e0", font=("Arial", 12)).pack(pady=10)

        # This button allows the user to select the private key file to decrypt the challenge
        key_button = tk.Button(self.login_window, text="Select Key File", command=lambda: self.decrypt_challenge(challenge, challenge_id, self.login_window), bg="#808080", fg="white", font=("Arial", 12, "bold"), padx=20, pady=10)  # Create a button to select the key file
        key_button.pack(pady=20)  # Pack the button with some padding
        logging.info("Login window displayed with encrypted challenge.")  # Log the display of the login window

    def is_challenge_valid(self):
        # Check if the challenge is within a valid time frame (e.g., 60 seconds)
        return (time.time() - self.challenge_time) < 60

    def handle_failed_attempt(self):
        self.failed_attempts += 1  # Increment the failed attempts counter
        self.lockout_duration = min(30, 2 ** self.failed_attempts)  # Calculate the lockout duration with a max of 30 seconds
        logging.warning(f"Authentication failed. Locking out for {self.lockout_duration} seconds.")  # Log the lockout
        self.after(self.lockout_duration * 1000, self.reset_lockout)  # Set a timer to reset the lockout

    def reset_lockout(self):
        self.lockout_duration = 0  # Reset the lockout duration
        logging.info("Lockout reset.")  # Log the reset

    def decrypt_challenge(self, encrypted_challenge, input_challenge_id, window):
        if self.lockout_duration > 0:
            messagebox.showerror("Login", f"Locked out for {self.lockout_duration} seconds.")  # Show an error message if locked out
            logging.warning("User attempted to log in during lockout period.")  # Log the attempt
            return  # Exit the function if locked out

        if not self.is_challenge_valid():
            messagebox.showerror("Login", "Challenge expired!")  # Show an error message if the challenge is expired
            logging.warning("Challenge expired.")  # Log the expiration
            return  # Exit the function if the challenge is expired

        if input_challenge_id != self.challenge_id:
            messagebox.showerror("Login", "Invalid Challenge ID!")  # Show an error message if the challenge ID is invalid
            logging.warning("Invalid Challenge ID.")  # Log the invalid challenge ID attempt
            return  # Exit the function if the challenge ID is invalid

        file_path = filedialog.askopenfilename(filetypes=[("PEM files", "*.pem")])  # Open a file dialog to select the key file
        if file_path:
            try:
                with open(file_path, 'rb') as key_file:
                    private_key = load_pem_private_key(key_file.read(), password=None)  # Load the private key from the file
                decrypted_challenge = private_key.decrypt(
                    base64.b64decode(encrypted_challenge),
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),  # Use MGF1 with SHA256
                        algorithm=hashes.SHA256(),  # Use SHA256 for the padding algorithm
                        label=None
                    )
                )  # Decrypt the challenge
                print(f"Decrypted Challenge for selected Admin: {base64.b64encode(decrypted_challenge).decode()}")  # Print the decrypted challenge
            except Exception as e:
                messagebox.showerror("Login", f"Error during decryption: {str(e)}")  # Show an error message if decryption fails
                logging.error(f"Decryption error: {str(e)}")  # Log the error
                print(f"Decryption attempt failed with error: {str(e)}")  # Print the error
                self.handle_failed_attempt()  # Handle the failed attempt
                return  # Exit the function after showing the error

            if decrypted_challenge == self.challenge:
                messagebox.showinfo("Login", "Authentication Successful!")  # Show a success message if authentication is successful
                logging.info("Authentication successful.")  # Log the success
                window.destroy()  # Close the login window
                self.destroy()  # Close the main application window
                subprocess.Popen(['python', 'trainer_ui.py'])  # Redirect to data.py
            else:
                self.handle_failed_attempt()  # Handle the failed attempt
                messagebox.showerror("Login", "Authentication Failed!")  # Show an error message if authentication fails
                logging.warning("Authentication failed.")  # Log the failure
        else:
            messagebox.showinfo("Login", "No Key File Selected")  # Show a message if no key file is selected

if __name__ == "__main__":
    app = App()  # Create an instance of the App class
    app.mainloop()  # Start the main event loop
