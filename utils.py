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
        default_path = "/Volumes/NO NAME"
        while True:
            volume_path = input(f"Please enter the volume path assigned to Busy Tag (or press Enter for '{default_path}'): ").strip()

            # Use default if user just pressed Enter
            if not volume_path:
                volume_path = default_path

            if os.path.exists(volume_path):
                print(f"Ok.")
                return volume_path
            else:
                print(f"Volume {volume_path} does not exist. Please enter a valid path.")

# Keep the old function for backwards compatibility
def get_drive_letter():
    return get_volume_path()

def transfer_file(source_path, destination_folder, new_name):
    import shutil
    try:
        if not os.path.exists(source_path):
            print(f"Error: Source file not found at {source_path}")
            return None
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        destination_path = os.path.join(destination_folder, new_name)
        shutil.move(source_path, destination_path)

        return destination_path

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def delete_file(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)

            return True
        else:
            return False
    except Exception as e:
        print(f"An error occurred while deleting the file: {e}")

        return False