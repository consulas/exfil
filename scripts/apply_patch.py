#!/usr/bin/env python3
"""
Script: apply_patch.py
Usage: python3 apply_patch.py /path/to/patchfile.patch /path/to/destination
Description:
  Apply a git patch to a target repository.
  If the target repository is an empty folder, it will initialize a git repo.
"""

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser(description="Apply a git patch to the specified folder.")
    parser.add_argument("patch_path", help="Path to the git patch file")
    parser.add_argument("repo_path", help="Path to the target repository")
    args = parser.parse_args()

    patch_path = os.path.abspath(args.patch_path)
    repo_path = os.path.abspath(args.repo_path)

    # Check if patch file exists.
    if not os.path.isfile(patch_path):
        sys.exit("Error: Patch file does not exist.")

    # Create destination folder if it doesn't exist.
    if not os.path.exists(repo_path):
        os.makedirs(repo_path)

    # Change working directory to destination folder.
    os.chdir(repo_path)

    # Initialize a new git repository if one doesn't exist.
    if not os.path.isdir(os.path.join(repo_path, ".git")):
        init_result = subprocess.run(["git", "init"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if init_result.returncode != 0:
            sys.exit(f"Error initializing git repository: {init_result.stderr.strip()}")

    # Apply the patch.
    apply_cmd = ["git", "apply", "--whitespace=fix", patch_path]
    apply_result = subprocess.run(apply_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if apply_result.returncode != 0:
        sys.exit(f"Error applying patch: {apply_result.stderr.strip()}")

    print("Patch applied successfully.")

if __name__ == "__main__":
    main()
