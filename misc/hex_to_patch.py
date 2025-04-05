import os, sys
import argparse
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.util import hex_to_file

# Argument parser
parser = argparse.ArgumentParser(description="Convert hex to binary patch file.")
parser.add_argument("--patch_path", default="./temp/output_exfil.patch", help="Path to the output binary file (default: ./temp/output_exfil.patch)")
parser.add_argument("--hex_path", default="./temp/output_exfil.hex", help="Path to the input hex file (default: ./temp/output_exfil.hex)")
args = parser.parse_args()

# Execute the conversion
hex_to_file(args.hex_path, args.patch_path)
