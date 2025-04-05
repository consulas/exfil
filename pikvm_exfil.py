import time
import threading
import argparse
from src.util import process_image, get_delimiters, get_glyph_map, match_glyphs, image_has_diff, combine_string_arr, hex_to_file, CASE, GLYPHS
from src.pikvm import get_screenshot
import cv2

API_URL = "https://192.168.0.112/streamer/snapshot"
USERNAME = "admin"
PASSWORD = "admin"
INVERT = True # Use if darkmode
DEBUG = False
# Update crop dimensions
CROP_DIMENSIONS = (110, 80, 1710, 870)  # (x, y, length, height)

# Global Variables - Use locks to ensure timing
glyph_map = None
rows = None
cols = None
last_image = None
width = None
height = None
image_num = 0
image_lock = threading.Lock()
output = []
output_lock = threading.Lock()

def capture_screenshot(i, api_url, username, password, debug=False):
    global glyph_map, rows, cols, last_image, width, height, image_num, output
    # Function to handle screenshot capture in a separate thread
    image = get_screenshot(api_url, username, password)
    image = process_image(image, CROP_DIMENSIONS, invert=INVERT)

    # Compare to previous image
    parse = False
    parseNum = 0
    with image_lock:
        if image_has_diff(last_image, image): # Handle none types
            print(f"Iteration {i} has diff")
            last_image = image 
            parseNum = image_num
            image_num += 1
            parse = True
        # else: 
        #     print(f"Iteration {i} no diff")

    if parse:
        if debug: 
            cv2.imwrite(f"./temp/img_{parseNum}.png", image)
        row_delimiters = get_delimiters(image, axis=1, threshold=.99)
        col_delimiters = get_delimiters(image, axis=0, threshold=.93)
        # print(len(row_delimiters))
        # print(len(col_delimiters))

        # Set for first loop
        if glyph_map is None: 
            print("Get glyph map") 
            glyph_map, width, height = get_glyph_map(image, row_delimiters, col_delimiters)
            rows = len(row_delimiters)
            cols = len(col_delimiters)

        output_string = match_glyphs(image, glyph_map, row_delimiters, col_delimiters, width, height)

        with output_lock:
            output.append((parseNum, output_string))
        print(f"Parsed image {i}")

def main():
    parser = argparse.ArgumentParser(description="Exfil hex screenshots to patch files")
    parser.add_argument("--hex_file", default="./temp/output_exfil.hex", help="Path to the output hex file (default: ./temp/output.hex)")
    parser.add_argument("--patch_file", default="./temp/output_exfil.patch", help="Path to the output binary file (default: ./temp/output.patch)")
    args = parser.parse_args()

    time.sleep(2)
    i = 0
    start_time = time.time()
    interval = .1
    
    try:
        while True:
            current_time = time.time()
            next_start_time = start_time + (i + 1) * interval
            
            # Sleep until the next time to start the thread
            sleep_time = next_start_time - current_time
            if sleep_time > 0:
                time.sleep(sleep_time)
            
            # Create a new thread for each screenshot capture
            threading.Thread(target=capture_screenshot, args=(i, API_URL, USERNAME, PASSWORD, DEBUG), daemon=True).start()
            i += 1
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
    finally:
        output_arr = sorted(output, key=lambda x: x[0])
        output_arr = [s[1] for s in output_arr]
        [print(len(s)) for s in output_arr]

        # Combine into one string based on overlap of n (cols)
        hex_string = combine_string_arr(output_arr, cols, debug=DEBUG)
        hex_string = hex_string[len(GLYPHS):].strip()

        # Write to hex and patch files
        with open(args.hex_file, "w") as file:
            file.write(hex_string)
        hex_to_file(args.hex_file, args.patch_file)

if __name__ == "__main__":
    main()
