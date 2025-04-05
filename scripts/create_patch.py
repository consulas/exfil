#!/usr/bin/env python3
"""
Script: create_patch.py
Usage: python3 create_patch.py /path/to/repo output.patch [--exclude folder1 file2 ...]
Description:
  Create a git patch comparing an existing repository to an empty repo.
  It excludes any files/folders specified via --exclude.
"""

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import argparse
import subprocess
from src.util import file_to_hex

def validate_repo_path(repo_path: str) -> str:
    """
    Validates the provided path is a git repository.
    Returns the absolute path of the repository if valid.
    """
    if not os.path.isdir(repo_path):
        sys.exit("Error: Provided repo path does not exist.")
    if not os.path.isdir(os.path.join(repo_path, ".git")):
        sys.exit("Error: Provided path is not a valid git repository.")
    return os.path.abspath(repo_path)

def create_patch(repo_path: str, output_patch: str, commit_hash: str, exclude: list):
    """
    Creates a git patch comparing the current repository to the specified commit_hash
    Excludes specified files/folders and writes the patch to the output file.
    """

    # Initialize the diff command
    diff_cmd = ["git", "diff", "--binary", "--full-index", commit_hash, "HEAD"]

    # Append exclusion pathspecs if any
    if exclude:
        diff_cmd.append("--")
        for item in exclude:
            diff_cmd.append(f":(exclude){item}")

    try:
        # Execute the diff command and write the result to the patch file
        with open(output_patch, "w") as patch_file:
            result = subprocess.run(diff_cmd, cwd=repo_path, stdout=patch_file, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                sys.exit(f"Error generating patch: {result.stderr.strip()}")
    except Exception as e:
        sys.exit(f"Failed to create patch file: {str(e)}")


def main():
    parser = argparse.ArgumentParser(description="Create a git patch from the specified commit_hash.")
    parser.add_argument("repo_path", help="Path to the existing git repository")
    parser.add_argument("--commit_hash", default="4b825dc642cb6eb9a060e54bf8d69288fbee4904", help="Hash to generate patch file from (default: empty hash)")
    parser.add_argument("--patch_path", default="./temp/output_base.patch", help="Path to the output binary file (default: ./temp/output.patch)")
    parser.add_argument("--hex_path", default="./temp/output_base.hex", help="Path to the output hex file (default: ./temp/output.hex)")
    parser.add_argument("--exclude", nargs="*", default=[], help="List of files/folders to exclude from the patch")
    args = parser.parse_args()

    # Validate repository path
    repo_path = validate_repo_path(args.repo_path)
    patch_path = os.path.abspath(args.patch_path)
    hex_path = os.path.abspath(args.hex_path)

    # Create the patch file
    create_patch(repo_path, patch_path, args.commit_hash, args.exclude)
    print(f"Patch file created at: {patch_path}")

    # Create a hex file
    file_to_hex(patch_path, hex_path)
    print(f"Hex file created at: {hex_path}")

if __name__ == "__main__":
    main()
