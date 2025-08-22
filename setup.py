import subprocess
import sys
import os
from pathlib import Path

def install_dependencies():
    print("Installing dependencies...")
    
    dependencies = [
        "tkinterdnd2==0.3.0",
        "asttokens",
        "datasets", 
        "huggingface-hub",
        "matplotlib",
        "networkx",
        "numpy",
        "pydot",
        "requests",
        "tokenizers",
        "torch",
        "tqdm",
        "rich",
        "seqeval",
        "transformers==4.46.1",
        "xdis>=6.1.4",
        "click"
    ]
    
    for dep in dependencies:
        try:
            print(f"Installing {dep}...")
            subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {dep}: {e}")
            return False
    
    return True

def install_pylingual():
    print("Installing pylingual from source...")
    current_dir = Path(__file__).parent
    pylingual_dir = current_dir / "pylingual-main"
    
    if not pylingual_dir.exists():
        print("ERROR: pylingual-main directory not found!")
        return False
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "poetry>=2.0"], check=True)
        subprocess.run([sys.executable, "-m", "pip", "install", "-e", str(pylingual_dir)], check=True)
        print("Pylingual installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install pylingual: {e}")
        return False

def run_gui():
    print("Starting Auto Dump GUI...")
    try:
        subprocess.run([sys.executable, "auto_dump_gui.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to start GUI: {e}")

def main():
    print("=== Auto Dump Setup ===")
    print("1. Install dependencies and run GUI")
    print("2. Just run GUI")
    
    choice = input("Enter choice (1/2): ").strip()
    
    if choice == "1":
        if install_dependencies() and install_pylingual():
            print("Setup completed successfully!")
            run_gui()
        else:
            print("Setup failed!")
    elif choice == "2":
        run_gui()
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    main()
