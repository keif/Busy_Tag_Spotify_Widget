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

- Python 3.6 or higher
- `Pillow` (PIL Fork) - Python Imaging Library
- `requests` for API calls
- `python-dotenv` for environment variable management
- A Busy Tag device connected to your computer.
- Spotify Client ID
- Spotify account

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
3. Install the required dependencies:
	Use `pip` to install the necessary packages.

	```
	pip install pillow requests python-dotenv
	```

4. Ensure the default font file `MontserratBlack-3zOvZ.ttf` is in the project directory.

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
