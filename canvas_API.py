from _canvas_pb2 import CanvasRequest, CanvasResponse
import requests

CANVASES_URL = 'https://spclient.wg.spotify.com/canvaz-cache/v0/canvases'

def get_canvases(tracks, access_token):
    canvas_request = CanvasRequest()

    for track in tracks:
        spotify_track = CanvasRequest.Track()
        spotify_track.track_uri = track['track']['uri']
        canvas_request.tracks.append(spotify_track)

    request_bytes = canvas_request.SerializeToString()

    headers = {
        'accept': 'application/protobuf',
        'content-type': 'application/x-www-form-urlencoded',
        'accept-language': 'en',
        'user-agent': 'Spotify/8.5.49 iOS/Version 13.3.1 (Build 17D50)',
        'accept-encoding': 'gzip, deflate, br',
        'authorization': f'Bearer {access_token}',
    }

    try:
        response = requests.post(CANVASES_URL, data=request_bytes, headers=headers)

        if response.status_code != 200:
            print(f"ERROR {CANVASES_URL}: {response.status_code} {response.reason}")
            if response.json().get('error'):
                print(response.json()['error'])
            return None
        else:
            canvas_response = CanvasResponse()
            canvas_response.ParseFromString(response.content)
            return canvas_response

    except requests.RequestException as error:
        print(f"ERROR {CANVASES_URL}: {error}")
        return None