import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import time
from src.pikvm import get_screenshot
from src.util import process_image, get_delimiters, get_glyph_map, match_glyphs, CASE

# Scroll to the up to get the first line / first character for the glyph map

# Constants
API_URL = "https://192.168.0.112/streamer/snapshot"
USERNAME = "admin"
PASSWORD = "admin"
INVERT = True # Use if darkmode
DEBUG = True
# Update crop dimensions
CROP_DIMENSIONS = (110, 80, 1710, 870)  # (x, y, length, height)

def main():
    # Get screenshot
    start_time = time.time()
    image = get_screenshot(API_URL, USERNAME, PASSWORD)
    if image is None:
        return
    print("Get Screenshot", time.time() - start_time)

    # Convert to greyscale, scale, etc.
    image = process_image(image, CROP_DIMENSIONS, invert=INVERT, debug=DEBUG)
    print("Process Image", time.time() - start_time)

    # Find row and column delimiters
    row_delimiters = get_delimiters(image, axis=1, threshold=.999, debug=DEBUG)
    col_delimiters = get_delimiters(image, axis=0, threshold=.97, debug=DEBUG)
    print(len(row_delimiters))
    print(len(col_delimiters))
    print("Find delimiters", time.time() - start_time)

    # Get glyph map from first row
    glyph_map, width, height = get_glyph_map(image, row_delimiters, col_delimiters, debug=False)
    print("Get Glyph Map", time.time() - start_time)

    # Get cells from image
    output_string = match_glyphs(image, glyph_map, row_delimiters, col_delimiters, width, height, debug=False)
    print("Match Glyphs", time.time() - start_time)

    #
    # Test against ground truth
    #
    # Get ground truth
    with open("./temp/test.hex", "r") as f:
        ground_truth_lines = f.readlines()
    ground_truth_string = ''.join(ground_truth_lines)
    output_string = output_string[17:].strip()

    if output_string in ground_truth_string:
        print("Match:")
        print(output_string)
    else: 
        print("No Match:")
        print("Ground Truth")
        print(ground_truth_string)
        print("Output")
        print(output_string)

if __name__ == "__main__":
    main()
