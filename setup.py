"""
py2app build script for BusyTag Spotify Widget

Build with:
    python setup.py py2app

For development/testing:
    python setup.py py2app -A
"""
import os

from setuptools import setup

APP = ['main.py']
DATA_FILES = [
    'MontserratBlack-3zOvZ.ttf',
    'spotify_logo.png',
]

# Bundle the developer's local .env if it exists. It is gitignored, so a clean
# checkout or CI/release build simply skips it instead of failing on a missing
# file; the app prompts for the Spotify client ID at runtime when it is absent.
if os.path.exists('.env'):
    DATA_FILES.append('.env')

OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'AppIcon.icns',
    'plist': {
        'CFBundleName': 'BusyTag Spotify',
        'CFBundleDisplayName': 'BusyTag Spotify Widget',
        'CFBundleIdentifier': 'com.busytag.spotify-widget',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'LSBackgroundOnly': False,
        'NSHighResolutionCapable': True,
    },
    'packages': ['requests', 'PIL', 'dotenv'],
    'includes': [
        'auth',
        'spotify_api',
        'utils',
        'image_operations',
        'color_extractor',
        'busytag_refresh',
    ],
}

setup(
    app=APP,
    name='BusyTag Spotify',
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
