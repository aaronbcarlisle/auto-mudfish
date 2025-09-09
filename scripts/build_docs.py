#!/usr/bin/env python3
"""
Build script for Sphinx documentation.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def clean_docs():
    """Clean previous documentation builds."""
    docs_build_dir = Path("docs/build")
    if docs_build_dir.exists():
        print("Cleaning previous documentation build...")
        shutil.rmtree(docs_build_dir)
    
    docs_source_dir = Path("docs/source/modules")
    if docs_source_dir.exists():
        print("Cleaning previous API documentation...")
        shutil.rmtree(docs_source_dir)

def build_api_docs():
    """Generate API documentation using sphinx-apidoc."""
    print("Generating API documentation...")
    
    cmd = [
        'sphinx-apidoc',
        '-o', 'docs/source/modules',
        'src/auto_mudfish',
        'src/gui',
        '--separate'
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("API documentation generated successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to generate API documentation: {e}")
        return False

def build_docs():
    """Build the Sphinx documentation."""
    print("Building Sphinx documentation...")
    
    os.chdir("docs")
    
    cmd = [
        'sphinx-build',
        '-b', 'html',
        'source',
        'build'
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Documentation built successfully!")
        print(f"Output location: docs/build/index.html")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to build documentation: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False
    finally:
        os.chdir("..")

def main():
    """Main documentation build process."""
    print("Auto Mudfish Documentation Builder")
    print("==================================")
    
    # Check if Sphinx is installed
    try:
        import sphinx
        print(f"Sphinx version: {sphinx.__version__}")
    except ImportError:
        print("Sphinx not found. Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'sphinx', 'sphinx-rtd-theme'])
    
    # Clean previous builds
    clean_docs()
    
    # Generate API documentation
    if not build_api_docs():
        print("Failed to generate API documentation!")
        sys.exit(1)
    
    # Build documentation
    if build_docs():
        print("\nDocumentation build successful!")
        print("\nTo view the documentation:")
        print("1. Open docs/build/index.html in your web browser")
        print("2. Or serve it locally with: python -m http.server 8000 --directory docs/build")
        
        print("\nFiles created:")
        print("- docs/build/ (HTML documentation)")
        print("- docs/source/modules/ (API documentation source)")
        
    else:
        print("\nDocumentation build failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
