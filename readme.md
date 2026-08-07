# Busy Tag Spotify Widget
## Table of Contents

- [Busy Tag Spotify Widget](#busy-tag-spotify-widget)
	- [Table of Contents](#table-of-contents)
	- [Introduction](#introduction)
	- [Project Purpose](#project-purpose)
	- [Prerequisites](#prerequisites)
	- [Installation](#installation)
		- [Troubleshooting](#troubleshooting)
		- [Creating\_a\_Spotify\_Client\_ID](#creating_a_spotify_client_id)

## Introduction

The Busy Tag Spotify Widget is a Python-based application that fetches the currently playing track from Spotify account and displays it on your Busy Tag device. The widget displays the album image, track name, and artist information, updating automatically whenever the track changes. Additionally, the widget automatically extracts vibrant colors from album artwork and sets the BusyTag LED colors to match, creating an immersive visual experience.

## Project Purpose

The main goal of this project is to:

- Integrate with the Spotify API to fetch the current track information.

- Display album art, track name, and artist on a Busy Tag device.

- Automatically extract and apply vibrant LED colors from album artwork to match the displayed track.

- Automatically update the displayed information and LED colors when the track changes or when playback is paused or resumed.

## Prerequisites

To run this script, ensure you have the following installed:

- Python 3.11 or higher
- [`uv`](https://docs.astral.sh/uv/) for dependency and environment management
- A Busy Tag device connected to your computer.
- Spotify Client ID
- Spotify account

Runtime dependencies (`Pillow`, `requests`, `python-dotenv`) are declared in
`pyproject.toml` and pinned in `uv.lock` — `uv` installs them for you.

## Installation
 
  To get started with this Python script, follow these steps:

1. **Clone the repository:**
   First, clone the repository from GitHub to your local machine.
   ```
   git clone https://github.com/busy-tag/Busy_Tag_Spotify_Widget.git
2. Navigate to the cloned repository:

	```
	cd Busy_Tag_Spotify_Widget.git
	```
3. Install the dependencies:
	`uv` reads `pyproject.toml`/`uv.lock`, provisions the correct Python
	version (from `.python-version`), and creates the virtual environment.

	```
	uv sync
	```

4. Ensure the default font file `MontserratBlack-3zOvZ.ttf` is in the project directory.

5. Run the widget:

	```
	uv run python main.py
	```

> Not using `uv`? A generated `requirements.txt` is provided for pip users:
> `pip install -r requirements.txt`. Note it is auto-generated from `uv.lock` —
> edit dependencies in `pyproject.toml`, not `requirements.txt`.

## Configuration

The script provides several customizable parameters:

• **Client ID:** You can provide a custom Spotify Client ID or use the default ( `Use of default Spotify Client ID requires approval, contact hello@busy-tag.com for approval`).

• **Volume Path:** On macOS/Linux, the default path is `/Volumes/NO NAME`. On Windows, you'll be prompted for the drive letter (e.g., `D`). Press Enter to use the default on macOS.

• **Image Processing:** Customize how the album art and text are displayed by adjusting parameters in `image_operations.py`.

• **LED Color Extraction:** The widget automatically extracts vibrant colors from album artwork. You can customize the extraction mode in `image_operations.py` (options: `vibrant`, `dominant`, `complementary`, `bright`). See `busytag_config_examples/` for BusyTag config structure reference.


## Usage
1. **Execute the script:**
You can run the script from the command line:
```
python main.py
```
2. **Provide Client ID:**
   
    The application will prompt you to provide your Spotify Client ID or use the default.
         
3. **Provide Volume Path:**

	Enter the volume path assigned to the Busy Tag device when prompted. On macOS, press Enter to use the default `/Volumes/NO NAME`, or enter a custom path. On Windows, enter the drive letter (e.g., `D`).

4. **Automatic Operation:**

	The widget will start fetching the current Spotify track information, updating the Busy Tag device with the album art, track name, artist details, and automatically setting LED colors to match the album artwork.
	
### Example

After running the script, you should see output similar to this in your terminal:
```
Please enter your Spotify Client ID (press Enter to use the default):
Authorization: Ok.
Please enter the volume path assigned to Busy Tag (or press Enter for '/Volumes/NO NAME'):
Ok.
Track changed.
Now playing: Shape of You by Ed Sheeran
Image saved successfully to: /Volumes/NO NAME/current_track_image.png
Extracted LED color from album art: #1FDB62
LED color set to: #1FDB62
Config written with LED color: #1FDB62
BusyTag config updated to display: current_track_image.png
```

The Busy Tag device will display the album art, track name, artist, and the LEDs will glow with colors extracted from the album artwork.
Sample:

<img src="/current_track_image_sample.png" alt="Current Track Image" width="300" height="390"/>

### Troubleshooting

If you encounter any issues, ensure:

All Python packages are installed correctly.

The font file (`MontserratBlack-3zOvZ.ttf`) is present in the project directory.

You have an active internet connection.

The drive letter is correct and the Busy Tag device is connected.

Your Spotify Client ID is correctly configured.

For any additional help, please open an issue in the repository or contact the maintainer.

### Creating_a_Spotify_Client_ID

Follow the steps below to obtain a Spotify Client ID.

**Step 1: Access the Spotify Developer Dashboard**

Go to the Spotify Developer Dashboard by navigating to https://developer.spotify.com/dashboard.

Log in to your Spotify account. If you don't have an account, you'll need to create one.

**Step 2: Create a New Spotify App**

Once logged in, click the `"Create an App` button on the dashboard.

A form will appear asking for the app details.

**Step 3: Fill in App Details**

**App Name:** Enter a name for your app. This can be anything descriptive, such as "Busy Tag Spotify Widget."

**App Description:** Provide a brief description of your app, e.g., "An app to display current Spotify track information."

**Redirect URI:** Enter http://127.0.0.1:8080/callback. This URI is required for the authentication process and should be exactly as shown.

**Web API:** Check the box to indicate that your app will use the Web API.

Once all fields are filled, click the `"Save"` button.

**Step 4: Access the App's Settings**

After creating the app, you'll be redirected to the app's page.

In the top-right corner of the app page, click the `"Settings"` button.

**Step 5: Obtain the Client ID**

In the `"Basic Information"` tab under Settings, you will find your `Client ID`.

Copy the Client ID as you'll need it to run the Busy_Tag_Spotify_Widget.

Your Spotify Client ID is now ready to be used with the Busy_Tag_Spotify_Widget. 

## Releasing

Versioning follows [Semantic Versioning](https://semver.org/); the version lives
in `pyproject.toml` and the py2app bundle reads it from there, so there is a single
source of truth.

`CHANGELOG.md` is generated from the Conventional Commit history with
[git-cliff](https://git-cliff.org/):

```
uv run git-cliff -o CHANGELOG.md   # regenerate the full changelog
uv run git-cliff --latest          # preview notes for the pending release
```

To cut a release (order matters — the tag must land on the commit that already
contains the finalized changelog):

1. Bump `version` in `pyproject.toml`.
2. Regenerate the changelog for the new version and commit it. `--tag` asserts
   the version so the pending commits are filed under it before the tag exists:
   `uv run git-cliff --tag vX.Y.Z -o CHANGELOG.md`.
3. Tag that commit and push: `git tag vX.Y.Z && git push origin vX.Y.Z`.

Cut the tag from `main` after the changelog commit has merged, so the tag stays
on the mainline. Pushing a `v*` tag triggers `.github/workflows/release.yml`,
which builds the release notes and publishes a GitHub Release automatically.

### Signing and notarization (macOS)

The same `v*` tag also builds a code-signed, notarized `.app` on a macOS runner
and attaches it to the release (the `macos-app` job in `release.yml`). This needs
a one-time setup of five repository secrets under
**Settings → Secrets and variables → Actions**:

| Secret | How to obtain it |
|--------|------------------|
| `MACOS_CERTIFICATE` | In Keychain Access, export your **Developer ID Application** certificate (with its private key) as a `.p12`, then base64-encode it: `base64 -i cert.p12 \| pbcopy`. |
| `MACOS_CERTIFICATE_PWD` | The password you set when exporting the `.p12`. |
| `AC_API_KEY_ID` | App Store Connect → Users and Access → Integrations → App Store Connect API → your key's **Key ID**. |
| `AC_API_ISSUER_ID` | The **Issuer ID** shown at the top of that same page. |
| `AC_API_KEY_P8` | The full contents of the downloaded `AuthKey_XXXXXXXX.p8` file (downloadable only once). |

The App Store Connect API key needs at least the **Developer** role for notarization.

On a tag push the job runs: `py2app` build → code-sign every nested Mach-O and the
bundle under the hardened runtime (`entitlements.plist`) → `notarytool submit --wait`
→ `stapler staple` → zip and upload as `BusyTag-Spotify-vX.Y.Z.zip`.

**Verify a release end-to-end.** Download the zip from the published release and
confirm Gatekeeper accepts it on a machine that never built it:

```
unzip BusyTag-Spotify-vX.Y.Z.zip
codesign --verify --strict --verbose=2 "BusyTag Spotify.app"
xcrun stapler validate "BusyTag Spotify.app"
spctl --assess --type execute --verbose "BusyTag Spotify.app"
# expected: "accepted" with "source=Notarized Developer ID"
```

**If notarization fails**, the workflow log prints a submission id. Pull the
per-file details with:

```
xcrun notarytool log <submission-id> \
  --key AuthKey.p8 --key-id "$AC_API_KEY_ID" --issuer "$AC_API_ISSUER_ID"
```

Most failures are a missing entitlement or an unsigned nested binary — fixable in
`entitlements.plist` or the signing step of the workflow.
