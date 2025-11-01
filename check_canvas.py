#!/usr/bin/env python3
"""
Quick script to check if a specific track has a canvas video available.
"""

import os
from dotenv import load_dotenv
from auth import authorize_user, get_access_token
from spotify_api import get_current_track
from save_canvas import get_canvas_url

# Load environment variables
load_dotenv()

client_id = os.getenv('SPOTIFY_CLIENT_ID') or "1f2af53deb5d4338b7dc8dd2bc1d2c96"

print("Getting Spotify authorization...")
auth_code, code_verifier = authorize_user(client_id)
if auth_code:
    access_token = get_access_token(client_id, auth_code, code_verifier)
else:
    print("Failed to authorize. Exiting...")
    exit(1)

print("\nFetching currently playing track...")
track_info, status_code = get_current_track(access_token)

if track_info and 'item' in track_info:
    track_name = track_info['item']['name']
    artist_name = track_info['item']['artists'][0]['name']
    track_uri = track_info['item']['uri']

    print(f"\nCurrently playing:")
    print(f"  Track: {track_name}")
    print(f"  Artist: {artist_name}")
    print(f"  URI: {track_uri}")

    print(f"\nChecking for canvas video...")
    canvas_url = get_canvas_url(track_uri, access_token)

    if canvas_url:
        print(f"\n✓ Canvas video found!")
        print(f"  URL: {canvas_url}")
    else:
        print(f"\n✗ No canvas video available for this track")
        print(f"\nNote: Not all tracks have canvas videos.")
        print(f"Try playing a different track and run this script again.")
else:
    print("No track currently playing")
