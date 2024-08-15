import os

def prompt_for_client_id():
    client_id = input("Please enter your Spotify CLIENT_ID: ")
    return client_id

def check_busy_tag_connection():
    is_connected = input("Is the BusyTag connected? (y/n): ").strip().lower() == 'y'
    drive_letter = None
    if is_connected:
        drive_letter = input("Please enter the drive letter of the BusyTag (e.g., E): ").strip().upper()
        if not os.path.exists(f"{drive_letter}:/"):
            print(f"Drive {drive_letter}:/ does not exist. Please check the drive letter and try again.")
            return None, None
    return is_connected, drive_letter

def get_drive_letter():
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