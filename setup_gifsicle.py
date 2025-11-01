import os
import sys
import shutil
import subprocess
import platform

def setup_gifsicle():
    # Try to find gifsicle in the system PATH first (for macOS/Linux)
    gifsicle_path = shutil.which('gifsicle')

    if gifsicle_path:
        return gifsicle_path

    # Check common installation paths on macOS
    if platform.system() == 'Darwin':
        homebrew_paths = [
            '/opt/homebrew/bin/gifsicle',  # Apple Silicon Macs
            '/usr/local/bin/gifsicle'       # Intel Macs
        ]
        for path in homebrew_paths:
            if os.path.exists(path):
                return path

    # Windows-specific bundled gifsicle
    if platform.system() == 'Windows':
        if getattr(sys, 'frozen', False):
            exe_dir = os.path.dirname(sys.executable)
        else:
            exe_dir = os.path.dirname(os.path.abspath(__file__))

        bundled_gifsicle_path = os.path.join(exe_dir, 'resources', 'gifsicle', 'gifsicle.exe')
        destination = os.path.join(os.environ['USERPROFILE'], 'gifsicle')
        gifsicle_exe_path = os.path.join(destination, 'gifsicle.exe')

        try:
            if os.path.exists(bundled_gifsicle_path):
                os.makedirs(destination, exist_ok=True)
                shutil.copy(bundled_gifsicle_path, gifsicle_exe_path)
                return gifsicle_exe_path
        except Exception as e:
            print(f"Error setting up gifsicle: {e}")
            return None

    # If we reach here, gifsicle was not found
    print("Gifsicle not found. Please install it:")
    print("  macOS: brew install gifsicle")
    print("  Linux: sudo apt-get install gifsicle")
    print("  Windows: bundled version should be in resources/gifsicle/")
    return None

def run_gifsicle(command_args):
    gifsicle_path = setup_gifsicle()

    if not gifsicle_path:
        print("Gifsicle setup failed. Cannot proceed with running gifsicle.")
        return None

    command = [gifsicle_path] + command_args
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout

    except subprocess.CalledProcessError as e:
        print(f"Gifsicle command failed with error: {e.stderr}")
        return None

    except Exception as e:
        print(f"Error running gifsicle: {e}")
        return None