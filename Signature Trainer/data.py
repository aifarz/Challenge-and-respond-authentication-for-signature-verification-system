import os
import cv2  # Importing the OpenCV library for image processing

def load_signatures(directory_path):
    """
    Loads signature images from a specified directory, distinguishing between genuine and forged.

    Args:
    directory_path (str): The path to the directory containing subdirectories of individuals' signatures.

    Returns:
    list: A list of loaded signature images in grayscale.
    list: A list of labels indicating whether each signature is genuine (0) or forged (1).
    """
    signatures = []  # List to store the loaded signature images
    labels = []  # List to store the labels (0 for genuine, 1 for forged)

    # Loop through all subdirectories in the given directory, each representing a person
    for person_folder in os.listdir(directory_path):
        person_path = os.path.join(directory_path, person_folder)  # Path to the person's folder

        # Check if the current path is indeed a directory (to avoid processing any files)
        if os.path.isdir(person_path):
            # Process each file in the person's directory
            for filename in os.listdir(person_path):
                file_path = os.path.join(person_path, filename)  # Full path to the file

                # Load the image in grayscale to reduce complexity
                image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)

                # Determine the label based on the file name
                if filename.startswith('original_'):
                    labels.append(0)  # Label as 0 for genuine signatures
                elif filename.startswith('forgeries_'):
                    labels.append(1)  # Label as 1 for forged signatures
                else:
                    continue  # Skip files that do not match the expected naming convention

                # Add the loaded image to the list of signatures
                signatures.append(image)

    return signatures, labels

# Usage example
directory_path = 'Data'  # Data directory
signatures, labels = load_signatures(directory_path)
print(f"Loaded {len(signatures)} signatures.")
print(f"Labels count - Genuine: {labels.count(0)}, Forged: {labels.count(1)}")
