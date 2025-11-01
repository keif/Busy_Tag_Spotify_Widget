import time
import requests

def get_current_track(access_token):
    endpoint = "https://api.spotify.com/v1/me/player/currently-playing"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    try:
        response = requests.get(endpoint, headers=headers)

        if response.status_code == 401:
            print("Access token expired. Reauthorizing...")
            return None, 401

        if response.status_code == 204:
            print("No track currently playing.")
            time.sleep(10)
            return None, response.status_code

        if response.status_code == 200:
            track_info = response.json()

            if track_info.get('currently_playing_type') == 'ad':
                print("Currently playing an Ad...")
                time.sleep(10)
                return None, response.status_code

            if track_info['item'] is None:
                print("No track information available.")
                return None, response.status_code

            track_name = track_info['item']['name']
            artist_name = track_info['item']['artists'][0]['name']
            return track_info, response.status_code

        print(f"Unexpected status code: {response.status_code}")
        return None, response.status_code

    except requests.exceptions.RequestException as e:
        print(f"Error occurred while trying to get current track: {e}")
        return None, None

def get_audio_features(access_token, track_id):
    """
    Get audio features for a track including BPM, energy, danceability, etc.

    Args:
        access_token: Spotify access token
        track_id: Spotify track ID

    Returns:
        dict: Audio features or None if failed
    """
    endpoint = f"https://api.spotify.com/v1/audio-features/{track_id}"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    try:
        response = requests.get(endpoint, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to get audio features: {response.status_code}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error getting audio features: {e}")
        return None