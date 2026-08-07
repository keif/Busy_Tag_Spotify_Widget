"""
py2app build script for BusyTag Spotify Widget

Build with:
    python setup.py py2app

For development/testing:
    python setup.py py2app -A
"""
import os
import tomllib

from py2app.build_app import py2app as _py2app_command
from setuptools import setup

# Single source of truth for the version: pyproject.toml. Keeps the app bundle's
# CFBundleVersion in lockstep with the packaging metadata (Python 3.11+ ships
# tomllib in the stdlib, which matches requires-python).
with open('pyproject.toml', 'rb') as _f:
    VERSION = tomllib.load(_f)['project']['version']


class BuildApp(_py2app_command):
    """py2app build command that tolerates a PEP 621 pyproject.toml.

    setuptools populates ``distribution.install_requires`` from
    ``[project].dependencies`` (which uv requires), but py2app refuses to run
    when that field is set. The runtime dependencies are already vendored into
    the bundle via the ``packages``/``includes`` options below, so we clear the
    field before py2app inspects it in ``finalize_options``.
    """

    def finalize_options(self):
        self.distribution.install_requires = None
        super().finalize_options()


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
        'CFBundleVersion': VERSION,
        'CFBundleShortVersionString': VERSION,
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
    cmdclass={'py2app': BuildApp},
)
