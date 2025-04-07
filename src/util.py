import os
import cv2
import numpy as np
# import cupy as cp
from collections import Counter

# Constants
# GLYPH_ORDER = "1234567890ABCDEF "
GLYPHS = "1234567890abcdef "
CASE = any(c.isupper() for c in GLYPHS)
USE_GPU = False

def file_to_hex(patch_file, hex_file):
    """Convert a file to a hexadecimal representation and save it in uppercase."""
    with open(patch_file, 'rb') as f:
        hex_data = f.read().hex()

    # Write GLYPH_ORDER followed by the hex data to the file
    with open(hex_file, 'w') as f:
        f.write(GLYPHS + "\n")
        f.write(hex_data.upper() if CASE else hex_data)

def hex_to_file(hex_file, patch_file):
    """Convert a hexadecimal file back to its original format."""
    with open(hex_file, 'r') as f:
        hex_data = f.read()

    with open(patch_file, 'wb') as f:
        f.write(bytes.fromhex(hex_data))

def process_image(image, crop_box, greyscale=True, invert=False, scale_factor=4, threshold=125, debug=False):
    """Process image by cropping, inverting, scaling, and binary b/w"""
    if debug:
        cv2.imwrite("./temp/img_base.png", image)

    x, y, w, h = crop_box
    image = image[y:y+h, x:x+w]

    # Convert to grayscale
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Invert colors if needed
    if invert:
        image = cv2.bitwise_not(image)

    # Resize image
    image = cv2.resize(image, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_LINEAR)

    # Apply binary threshold
    _, image = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)

    if debug: 
        cv2.imwrite("./temp/img_processed.png", image)

    return image

def get_delimiters(img, axis, threshold=1, debug=False):
    """Find delimiters (row or column boundaries) based on white space and return gaps between them."""
    # Calculate the threshold value
    max_sum = 255 * img.shape[axis] * threshold
    
    # Sum pixels along the specified axis (rows or columns)
    line_sums = np.sum(img, axis=axis)
    
    # Find indices where the sum exceeds the threshold
    delimiters = np.where(line_sums >= max_sum)[0]

    # Find gaps between non-consecutive delimiters
    gaps = [(delimiters[i], delimiters[i+1]) for i in range(len(delimiters) - 1) if delimiters[i] + 1 != delimiters[i+1]]

    if debug:
        img_color = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        for delimiter in delimiters:
            start = (0, delimiter) if axis == 1 else (delimiter, 0)
            end = (img_color.shape[1], delimiter) if axis == 1 else (delimiter, img_color.shape[0])
            cv2.line(img_color, start, end, (255, 0, 0), 1)
        cv2.imwrite(f"./temp/img_delimited_axis{axis}.png", img_color)
    
    return gaps

def resize_glyph(img, width, height):
    if img.shape != (height, width):
        img = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)
    return img

def get_glyph_map(img, row_tuples, col_tuples, debug=False):
    row_start, row_end = row_tuples[0]
    shapes = []
    glyph_map = {}

    # Populate glyph map
    for char_idx, char in enumerate(GLYPHS):
        col_start, col_end = col_tuples[char_idx]
        glyph_image = img[row_start:row_end, col_start:col_end]
        glyph_map[char] = glyph_image
        shapes.append(glyph_image.shape)

    # Resize glyphs
    height, width = Counter(shapes).most_common(1)[0][0]
    for char in glyph_map:
        glyph_map[char] = resize_glyph(glyph_map[char], width, height)

    # Debug
    if debug:
        for char, glyph in glyph_map.items():
            cv2.imwrite(f"./temp/glyph_{char}.png", glyph)

    return glyph_map, width, height

def match_glyphs(image, glyph_map, row_tuples, col_tuples, width, height, debug=False):
    # Convert the entire glyph_map to NumPy float32 arrays at once
    grid_cells = []
    for row_idx, (row_start, row_end) in enumerate(row_tuples):
        for col_idx, (col_start, col_end) in enumerate(col_tuples):
            # Crop the cell using row and column delimiters
            glyph = image[row_start:row_end, col_start:col_end]
            glyph = resize_glyph(glyph, width, height)  # Assuming resize_glyph works with NumPy arrays
            grid_cells.append(glyph)  # Keep as NumPy array
            
            if debug:
                # Save the debug image using OpenCV
                cell_filename = f"./temp/glyph_row{row_idx+1}_col{col_idx+1}.png"
                cv2.imwrite(cell_filename, glyph)  # Directly save as NumPy array

    # Calculate squared error and determine best match cell
    template_chars = list(glyph_map.keys())
    if USE_GPU: 
        # Convert into cupy
        glyph_map = {char: cp.asarray(template.astype(cp.float32)) for char, template in glyph_map.items()}
        grid_cells = cp.array(grid_cells, dtype=cp.float32)
        template_arr = cp.array(list(glyph_map.values()))
        errors = cp.sum((grid_cells[:, None, :, :] - template_arr[None, :, :, :]) ** 2, axis=(2, 3))
        best_indices = cp.argmin(errors, axis=1)
        output = [template_chars[int(i)] for i in cp.asnumpy(best_indices)]
    else: 
        grid_cells = np.array(grid_cells, dtype=np.float32)
        template_arr = np.array(list(glyph_map.values()))
        errors = np.sum((grid_cells[:, None, :, :] - template_arr[None, :, :, :]) ** 2, axis=(2, 3))
        best_indices = np.argmin(errors, axis=1)
        output = [template_chars[i] for i in best_indices]

    output = "".join(output)
    return output

def image_has_diff(prev_image, image, threshold=.05):
    """Return true if diff > threshold"""
    if prev_image is None:
        return True 
    
    # Compute average difference
    diff = cv2.absdiff(prev_image, image)
    diff_ratio = np.count_nonzero(diff) / diff.size
    
    # Return True if the difference ratio exceeds the threshold
    return diff_ratio > threshold

def combine_string_arr(arr, n, debug=False):
    """Combine arr of strings together based on overlap of interval n"""
    def combine_strings(s1, s2, n):
        min_len = min(len(s1), len(s2))
        min_overlap = 0
        
        for i in range(n, min_len + 1, n):  # Check multiples of n
            if s1[-i:] == s2[:i]:  
                min_overlap = i
                break  # Stop at the first valid overlap (non-greedy)
        if debug:
            print(f"Overlap: {min_overlap}")
        return s1 + s2[min_overlap:]

    result = arr[0]
    for i in range(1, len(arr)):
        result = combine_strings(result, arr[i], n)
    
    return result
