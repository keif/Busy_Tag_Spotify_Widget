import os
import platform

def prompt_for_client_id():
    client_id = input("Please enter your Spotify CLIENT_ID: ")
    return client_id

def check_busy_tag_connection():
    is_connected = input("Is the BusyTag connected? (y/n): ").strip().lower() == 'y'
    volume_path = None
    if is_connected:
        if platform.system() == "Windows":
            volume_path = input("Please enter the drive letter of the BusyTag (e.g., E): ").strip().upper()
            if not os.path.exists(f"{volume_path}:/"):
                print(f"Drive {volume_path}:/ does not exist. Please check the drive letter and try again.")
                return None, None
        else:
            volume_path = input("Please enter the volume path of the BusyTag (e.g., /Volumes/BUSYTAG): ").strip()
            if not os.path.exists(volume_path):
                print(f"Volume {volume_path} does not exist. Please check the path and try again.")
                return None, None
    return is_connected, volume_path

def get_volume_path():
    system = platform.system()

    if system == "Windows":
        while True:
            drive_letter = input("Please enter the drive letter assigned to Busy Tag (e.g., D): ").upper()

            if len(drive_letter) == 1 and drive_letter.isalpha():
                drive_letter = f"{drive_letter}:"

                if os.path.exists(f"{drive_letter}\\"):
                    print(f"Ok.")
                    return drive_letter
                else:
                    print(f"Drive {drive_letter} does not exist. Please enter a valid drive letter.")
            else:
                print("Invalid input. Please enter a single letter (e.g., D).")
    else:  # macOS, Linux, etc.
        while True:
            volume_path = input("Please enter the volume path assigned to Busy Tag (e.g., /Volumes/BUSYTAG): ").strip()

            if os.path.exists(volume_path):
                print(f"Ok.")
                return volume_path
            else:
                print(f"Volume {volume_path} does not exist. Please enter a valid path.")

# Keep the old function for backwards compatibility
def get_drive_letter():
    return get_volume_path()