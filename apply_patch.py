#!/usr/bin/env python3
"""
Script: apply_patch.py
Usage: python3 apply_patch.py patchfile.patch /path/to/destination
Description:
  Apply a git patch to a destination folder to re-create the repository.
  If the destination folder is not a git repo, it will be initialized.
"""

import argparse
import subprocess
import os
import sys

def main():
    parser = argparse.ArgumentParser(
        description="Apply a git patch to re-create the repository in the destination folder."
    )
    parser.add_argument("patchfile", help="Path to the git patch file")
    parser.add_argument("destination_folder", help="Destination folder where the patch will be applied")
    args = parser.parse_args()

    # Get absolute paths for patch file and destination folder
    patchfile = os.path.abspath(args.patchfile)
    destination_folder = os.path.abspath(args.destination_folder)

    # Check if patch file exists.
    if not os.path.isfile(patchfile):
        sys.exit("Error: Patch file does not exist.")

    # Create destination folder if it doesn't exist.
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # Change working directory to destination folder.
    os.chdir(destination_folder)

    # Initialize a new git repository if one doesn't exist.
    if not os.path.isdir(os.path.join(destination_folder, ".git")):
        init_result = subprocess.run(["git", "init"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if init_result.returncode != 0:
            sys.exit(f"Error initializing git repository: {init_result.stderr.strip()}")

    # Apply the patch.
    apply_cmd = ["git", "apply", "--whitespace=fix", patchfile]
    apply_result = subprocess.run(apply_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if apply_result.returncode != 0:
        sys.exit(f"Error applying patch: {apply_result.stderr.strip()}")

    print("Patch applied successfully.")

if __name__ == "__main__":
    main()
