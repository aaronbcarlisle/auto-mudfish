#!/usr/bin/env python3
"""
Script to organize existing release files into the releases/ folder structure.
"""

import os
import shutil
from pathlib import Path

def organize_releases():
    """Move existing release files to the proper releases/ folder structure."""
    print("Organizing existing release files...")
    
    # Create releases directory if it doesn't exist
    releases_dir = Path("releases")
    releases_dir.mkdir(exist_ok=True)
    
    # Files to move and their target versions
    files_to_move = [
        ("RELEASE_NOTES_v1.0.0.md", "v1.0.0"),
    ]
    
    for filename, version in files_to_move:
        if os.path.exists(filename):
            # Create version directory
            version_dir = releases_dir / version
            version_dir.mkdir(exist_ok=True)
            
            # Move file
            target_path = version_dir / filename
            shutil.move(filename, target_path)
            print(f"Moved {filename} to {target_path}")
        else:
            print(f"File {filename} not found, skipping...")
    
    print("Release organization complete!")
    print("\nCurrent releases structure:")
    for version_dir in sorted(releases_dir.iterdir()):
        if version_dir.is_dir():
            print(f"  {version_dir.name}/")
            for file in sorted(version_dir.iterdir()):
                if file.is_file():
                    print(f"    {file.name}")

if __name__ == "__main__":
    organize_releases()
