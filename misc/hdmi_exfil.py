import cv2
import time
import numpy as np
import os
import nvidia.vpi as vpi

# Load all templates (characters "1234567890ABCDEF ")
template_folder = './templates'
templates = {}
characters = "1234567890ABCDEF "

# Initialize the CUDA device and context
device = vpi.Device(0)
context = device.create_context()

# Load templates into CUDA memory
for char in characters:
    img_path = os.path.join(template_folder, f"{char}.png")
    template_img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    
    # Convert the template image to VPI image and upload it to GPU
    templates[char] = vpi.asimage(template_img).to(device)

# Open the capture card (adjust device index if needed)
cap = cv2.VideoCapture(0)  # Try 1, 2, etc., if 0 doesn't work

# Set resolution (modify as per your capture card specs)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cap.set(cv2.CAP_PROP_FPS, 60)

if not cap.isOpened():
    print("Error: Could not open capture device.")
    exit()

frame_count = 0

# Function to match a single template (optimized using CUDA)
def template_match(image, template):
    # Convert to VPI image format
    vpi_img = vpi.asimage(image).to(device)

    # Perform template matching using VPI
    result = vpi_img.template_match(template)

    return result

def process_frame(frame):
    # Convert to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Coordinates of detected characters
    detected_string = ""

    # Grid dimensions
    grid_width = 30
    grid_height = 150

    # For each character in the 30x150 grid (adjust grid size as per your use case)
    for row in range(0, 1080, grid_height):  # 1080 is the frame height
        for col in range(0, 1920, grid_width):  # 1920 is the frame width
            # Crop the region corresponding to a character in the grid
            char_img = gray_frame[row:row + grid_height, col:col + grid_width]

            best_match = None
            best_score = -np.inf  # Initialize with worst score

            # Perform template matching for each character template (now loaded on CUDA)
            for char, template in templates.items():
                result = template_match(char_img, template)
                if result.score > best_score:
                    best_score = result.score
                    best_match = char

            detected_string += best_match

    return detected_string

def has_image_changed(prev_image, image, threshold=0.05):
    """Return true if diff > threshold"""
    if prev_image is None:
        return True 
    
    # Compute absolute difference
    diff = cv2.absdiff(prev_image, image)
    
    # Count nonzero pixels (differences)
    diff_ratio = np.count_nonzero(diff) / diff.size
    
    # Return True if the difference ratio exceeds the threshold
    return diff_ratio > threshold

# Initialize previous frame variable
prev_frame = None

while True:
    start_time = time.time()

    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    # Convert frame to grayscale for change detection
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Check if the image has changed compared to the previous frame
    if has_image_changed(prev_frame, gray_frame):
        # Process the frame if it has changed
        detected_string = process_frame(frame)
        print(f"Detected String: {detected_string}")
        
        # Save frame as image
        filename = f"frame_{frame_count:04d}.png"
        cv2.imwrite(filename, frame)
        print(f"Saved: {filename}")

    # Update previous frame
    prev_frame = gray_frame

    frame_count += 1

    # Display the frame (optional)
    cv2.imshow("Captured Frame", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
        break

    # Ensure 60 FPS capture
    elapsed_time = time.time() - start_time
    sleep_time = max(0, (1/60) - elapsed_time)
    time.sleep(sleep_time)

cap.release()
cv2.destroyAllWindows()
