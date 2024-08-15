import time
from auth import authorize_user, get_access_token
from spotify_api import get_current_track
from utils import prompt_for_client_id, check_busy_tag_connection, get_drive_letter
from image_operations import get_track_image, save_image, create_image_with_text

def main():
    default_client_id = "1f2af53deb5d4338b7dc8dd2bc1d2c96"

    client_id = input(f"Please enter your Spotify CLIENT_ID (or press Enter to use the default): ").strip()
    if not client_id:
        client_id = default_client_id
        print(f"Using default CLIENT_ID: {client_id}")
    else:
        print(f"Using provided CLIENT_ID: {client_id}")

    drive_letter = get_drive_letter()
    auth_code, code_verifier = authorize_user(client_id)
    if auth_code:
        access_token = get_access_token(client_id, auth_code, code_verifier)
    else:
        print("Failed to authorize. Exiting...")
        return

    current_track_name = None
    track_paused_printed = False
    track_resumed_printed = False

    try:
        while True:
            track_info, status_code = get_current_track(access_token)

            if status_code == 401:
                auth_code, code_verifier = authorize_user(client_id)
                if auth_code:
                    access_token = get_access_token(client_id, auth_code, code_verifier)
                    if not access_token:
                        print("Failed to reauthorize. Exiting...")
                        break
                else:
                    print("Failed to reauthorize. Exiting...")
                    break

            if track_info and 'item' in track_info:
                is_playing = track_info.get('is_playing', False)
                new_track_name = track_info.get('item', {}).get('name')

                if not is_playing:
                    if not track_paused_printed:
                        print("Track Paused.")
                        track_paused_printed = True
                        track_resumed_printed = False
                    time.sleep(0.5)
                    continue

                if is_playing and not track_resumed_printed:
                    print("Track Resumed.")
                    track_resumed_printed = True
                    track_paused_printed = False

                if new_track_name and "(feat." in new_track_name:
                    new_track_name = new_track_name.split("(feat.")[0].strip()

                if new_track_name and new_track_name != current_track_name:
                    current_track_name = new_track_name

                    track_info['item']['name'] = new_track_name
                    artist_name = track_info['item']['artists'][0]['name']

                    image = get_track_image(track_info)
                    if image:
                        print(f"Track changed.\nNow playing: {new_track_name} by {artist_name}")
                        save_image(image, "track_image.png")
                        create_image_with_text(track_info, "track_image.png", drive_letter)

                    track_paused_printed = False
                    track_resumed_printed = True

            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nProgram terminated by user.")

if __name__ == "__main__":
    main()