#!/usr/bin/env python3
"""
Script: create_patch.py
Usage: python3 create_patch.py /path/to/repo output.patch [--exclude folder1 file2 ...]
Description:
  Create a git patch comparing an existing repository to an empty repo.
  It excludes any files/folders specified via --exclude.
"""

import argparse
import subprocess
import os
import sys

def main():
    parser = argparse.ArgumentParser(description="Create a git patch comparing an existing repo to an empty repo.")
    parser.add_argument("repo_path", help="Path to the existing git repository")
    parser.add_argument("output_patch", help="Path to the output patch file")
    parser.add_argument("--exclude", nargs="*", default=[], help="List of files/folders to exclude from the patch")
    args = parser.parse_args()

    # Get absolute paths for input and output
    repo_path = os.path.abspath(args.repo_path)
    output_patch = os.path.abspath(args.output_patch)
    exclude = args.exclude

    # Check if repository exists and is a git repo
    if not os.path.isdir(repo_path):
        sys.exit("Error: Provided repo path does not exist.")
    if not os.path.isdir(os.path.join(repo_path, ".git")):
        sys.exit("Error: Provided path is not a valid git repository.")

    # Change working directory to the repository
    os.chdir(repo_path)

    # The hash for an empty tree in git is constant.
    empty_tree_hash = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"

    # Build the diff command with binary flag and full index for handling binary files.
    diff_cmd = ["git", "diff", "--binary", "--full-index", empty_tree_hash, "HEAD"]

    # Append exclusion pathspecs if any.
    if exclude:
        diff_cmd.append("--")
        for item in exclude:
            diff_cmd.append(f":(exclude){item}")

    try:
        with open(output_patch, "w") as patch_file:
            result = subprocess.run(diff_cmd, stdout=patch_file, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                sys.exit(f"Error generating patch: {result.stderr.strip()}")
    except Exception as e:
        sys.exit(f"Failed to create patch file: {str(e)}")

    print(f"Patch file created at: {output_patch}")

if __name__ == "__main__":
    main()
