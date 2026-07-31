import json
import os
from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFont

from busytag_refresh import refresh_busytag
from color_extractor import get_album_led_color, get_multiple_album_colors


def create_connection_lost_image(volume_path):
    """
    Create and display a 'Connection Lost...' image on the BusyTag with pulsing red LEDs.

    Args:
        volume_path: Path to the BusyTag volume
    """
    canvas_width = 240
    canvas_height = 280

    # Create black background
    canvas = Image.new('RGB', (canvas_width, canvas_height), (0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    font_path = "MontserratBlack-3zOvZ.ttf"

    # Draw "CONNECTION" and "LOST..." text
    try:
        title_font = ImageFont.truetype(font_path, 28)
        subtitle_font = ImageFont.truetype(font_path, 24)
    except OSError:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()

    # Calculate text positions for centering
    connection_text = "CONNECTION"
    lost_text = "LOST..."

    # Get text bounding boxes for centering
    conn_bbox = draw.textbbox((0, 0), connection_text, font=title_font)
    lost_bbox = draw.textbbox((0, 0), lost_text, font=subtitle_font)

    conn_width = conn_bbox[2] - conn_bbox[0]
    lost_width = lost_bbox[2] - lost_bbox[0]

    # Center horizontally, position vertically in middle of screen
    conn_x = (canvas_width - conn_width) // 2
    lost_x = (canvas_width - lost_width) // 2

    conn_y = 110
    lost_y = 150

    # Draw text with slight red tint for techy look
    draw.text((conn_x, conn_y), connection_text, font=title_font, fill=(255, 50, 50))
    draw.text((lost_x, lost_y), lost_text, font=subtitle_font, fill=(180, 180, 180))

    # Add some decorative elements for techy feel
    # Top and bottom red lines
    draw.rectangle([(20, 80), (220, 82)], fill=(255, 0, 0))
    draw.rectangle([(20, 198), (220, 200)], fill=(255, 0, 0))

    # Small blinking dots pattern
    for i in range(5):
        x = 60 + i * 30
        draw.ellipse([(x, 210), (x + 6, 216)], fill=(255, 0, 0) if i % 2 == 0 else (80, 0, 0))

    image_filename = "connection_lost.png"
    output_path = os.path.join(volume_path, image_filename)

    try:
        canvas.save(output_path)
        print(f"Connection lost image saved to: {output_path}")

        # Configure pulsing red LED pattern
        config_path = os.path.join(volume_path, "config.json")

        try:
            with open(config_path) as f:
                config = json.loads(f.read())
        except (OSError, json.JSONDecodeError):
            config = {
                "version": 3,
                "show_after_drop": False,
                "allow_usb_msc": True,
                "allow_file_server": False,
                "disp_brightness": 100
            }

        config['image'] = image_filename
        config['show_after_drop'] = False

        # Pulsing red LED pattern (dark red -> bright red -> dark red)
        config['activate_pattern'] = True
        config['pattern_repeat'] = 255  # Loop endlessly
        config['custom_pattern_arr'] = [
            {"led_bits": 127, "color": "330000", "speed": 50, "delay": 400},
            {"led_bits": 127, "color": "FF0000", "speed": 50, "delay": 400},
            {"led_bits": 127, "color": "330000", "speed": 50, "delay": 400},
        ]

        # Disable solid color
        config['solid_color'] = {"led_bits": 0, "color": "000000"}

        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
            f.flush()
            os.fsync(f.fileno())

        print("BusyTag configured with pulsing red LED pattern")

        # Trigger display refresh
        volume_name = os.path.basename(volume_path)
        refresh_busytag(volume_name=volume_name)

        return True
    except Exception as e:
        print(f"Error creating connection lost display: {e}")
        return False


def get_track_image(track_info):
    try:
        image_url = track_info['item']['album']['images'][0]['url']
        response = requests.get(image_url)
        response.raise_for_status()

        image = Image.open(BytesIO(response.content))
        return image

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the image: {e}")
        return None

def save_image(image, path):
    try:
        image.save(path)
    except Exception as e:
        print(f"Error saving the image: {e}")

def update_busytag_config(volume_path, image_filename, led_color=None):
    """
    Update the BusyTag config.json to point to the new image and set LED color.

    Args:
        volume_path: Path to the BusyTag volume
        image_filename: Name of the image file to display
        led_color: Optional hex color string for LEDs (e.g., "FF0000")
    """
    config_path = os.path.join(volume_path, "config.json")

    try:
        # Read existing config
        with open(config_path) as f:
            content = f.read()

        # Try to parse JSON
        try:
            config = json.loads(content)
        except json.JSONDecodeError as je:
            print("Warning: config.json is malformed. Creating new config.")
            print(f"JSON Error: {je}")
            # Create a minimal valid config
            config = {
                "version": 3,
                "image": image_filename,
                "show_after_drop": False,
                "allow_usb_msc": True,
                "allow_file_server": False,
                "disp_brightness": 100
            }

        # Update the image field
        config['image'] = image_filename

        # Set show_after_drop to false - we trigger refresh via unmount/remount
        config['show_after_drop'] = False

        # Ensure required fields exist with proper structure
        if 'solid_color' not in config:
            config['solid_color'] = {"led_bits": 0, "color": "000000"}
        if 'activate_pattern' not in config:
            config['activate_pattern'] = False
        if 'pattern_repeat' not in config:
            config['pattern_repeat'] = 0
        if 'custom_pattern_arr' not in config:
            config['custom_pattern_arr'] = []

        # Update LED color if provided
        if led_color:
            config['solid_color']['led_bits'] = 127  # All 7 LEDs
            config['solid_color']['color'] = led_color
            config['activate_pattern'] = False  # Ensure patterns are disabled
            print(f"LED color set to: #{led_color}")

        # Write back the config with proper formatting
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
            f.flush()  # Ensure data is written to disk
            os.fsync(f.fileno())  # Force write to physical storage

        print(f"BusyTag config updated to display: {image_filename}")
        if led_color:
            print(f"Config written with LED color: #{led_color}")
        return True
    except Exception as e:
        print(f"Error updating BusyTag config: {e}")
        return False

def update_busytag_config_with_pattern(volume_path, image_filename, colors, bpm, speed=100):
    """
    Update BusyTag config.json with LED pattern animation based on BPM.

    Args:
        volume_path: Path to the BusyTag volume
        image_filename: Name of the image file to display
        colors: List of hex color strings for the pattern
        bpm: Beats per minute for timing the pattern
        speed: LED transition speed (0-255, default 100)
    """
    config_path = os.path.join(volume_path, "config.json")

    # Calculate delay based on BPM (milliseconds per beat)
    delay_ms = int(60000 / bpm) if bpm > 0 else 500

    try:
        # Read existing config
        with open(config_path) as f:
            content = f.read()

        # Try to parse JSON
        try:
            config = json.loads(content)
        except json.JSONDecodeError as je:
            print("Warning: config.json is malformed. Creating new config.")
            print(f"JSON Error: {je}")
            config = {
                "version": 3,
                "image": image_filename,
                "show_after_drop": False,
                "allow_usb_msc": True,
                "allow_file_server": False,
                "disp_brightness": 100
            }

        # Update the image field
        config['image'] = image_filename

        # Set show_after_drop to false - we trigger refresh via unmount/remount
        config['show_after_drop'] = False

        # Build pattern array from colors
        pattern_arr = []
        for color in colors:
            pattern_arr.append({
                "led_bits": 127,  # All 7 LEDs
                "color": color,
                "speed": speed,
                "delay": delay_ms
            })

        # Configure pattern mode
        config['activate_pattern'] = True
        config['pattern_repeat'] = 255  # Loop endlessly
        config['custom_pattern_arr'] = pattern_arr

        # Disable solid color when using patterns
        if 'solid_color' not in config:
            config['solid_color'] = {"led_bits": 0, "color": "000000"}
        else:
            config['solid_color']['led_bits'] = 0  # Turn off solid color

        # Write back the config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)
            f.flush()
            os.fsync(f.fileno())

        print("BusyTag config updated with LED pattern:")
        print(f"  - Colors: {', '.join(['#' + c for c in colors])}")
        print(f"  - BPM: {bpm} ({delay_ms}ms per beat)")
        return True
    except Exception as e:
        print(f"Error updating BusyTag config with pattern: {e}")
        return False


def create_image_with_text(track_info, image_path, volume_path, bpm=None):
    canvas_width = 240
    canvas_height = 280

    canvas = Image.new('RGB', (canvas_width, canvas_height), (0, 0, 0))

    try:
        track_image = Image.open(image_path)
    except OSError:
        print(f"Error opening the image at {image_path}")
        return

    album_image_height = 225
    album_image_width = 240

    track_image = track_image.resize((album_image_width, album_image_height))

    x_offset = (canvas_width - album_image_width) // 2
    y_offset = 0

    canvas.paste(track_image, (x_offset, y_offset))

    draw = ImageDraw.Draw(canvas)

    font_path = "MontserratBlack-3zOvZ.ttf"

    track_name = track_info['item']['name']
    artist_name = track_info['item']['album']['artists'][0]['name']

    if len(track_name) < 13:
        track_font_size = 24
        artist_font_size = 18
        text_y_track = album_image_height + y_offset
        text_y_artist = text_y_track + track_font_size + 5

        track_font = ImageFont.truetype(font_path, track_font_size)
        artist_font = ImageFont.truetype(font_path, artist_font_size)

        draw.text((50, text_y_track), track_name, font=track_font, fill=(255, 255, 255))
        draw.text((50, text_y_artist), artist_name, font=artist_font, fill=(128, 128, 128))

    elif 13 <= len(track_name) <= 16:
        track_font_size = 20
        artist_font_size = 14
        text_y_track = album_image_height + y_offset
        text_y_artist = text_y_track + track_font_size + 5

        track_font = ImageFont.truetype(font_path, track_font_size)
        artist_font = ImageFont.truetype(font_path, artist_font_size)

        draw.text((50, text_y_track), track_name, font=track_font, fill=(255, 255, 255))
        draw.text((50, text_y_artist), artist_name, font=artist_font, fill=(128, 128, 128))

    elif 16 < len(track_name) <= 20:
        track_font_size = 16
        artist_font_size = 12
        text_y_track = album_image_height + y_offset
        text_y_artist = text_y_track + track_font_size + 5

        track_font = ImageFont.truetype(font_path, track_font_size)
        artist_font = ImageFont.truetype(font_path, artist_font_size)

        draw.text((50, text_y_track), track_name, font=track_font, fill=(255, 255, 255))
        draw.text((50, text_y_artist), artist_name, font=artist_font, fill=(128, 128, 128))

    elif len(track_name) > 20:
        split_index = track_name.rfind(' ', 0, 21)
        if split_index == -1:
            split_index = 20 

        first_line = track_name[:split_index]
        second_line = track_name[split_index:].strip()

        track_font_size = 16
        artist_font_size = 10

        track_font = ImageFont.truetype(font_path, track_font_size)
        artist_font = ImageFont.truetype(font_path, artist_font_size)

        text_y_track = album_image_height + y_offset
        text_y_second_line = text_y_track + track_font_size + 5
        text_y_artist = text_y_second_line + track_font_size + 5

        draw.text((50, text_y_track), first_line, font=track_font, fill=(255, 255, 255))
        draw.text((50, text_y_second_line), second_line, font=track_font, fill=(255, 255, 255))
        draw.text((50, text_y_artist), artist_name, font=artist_font, fill=(128, 128, 128))

    try:
        spotify_logo = Image.open("spotify_logo.png")
        logo_size = (30, 30)
        spotify_logo = spotify_logo.resize(logo_size)

        logo_x = 13
        logo_y = canvas_height - 49

        canvas.paste(spotify_logo, (logo_x, logo_y), spotify_logo)
    except OSError:
        print("Error opening the Spotify logo image.")

    image_filename = "current_track_image.png"
    output_path = os.path.join(volume_path, image_filename)

    try:
        canvas.save(output_path)
        print(f"Image saved successfully to: {output_path}")

        # Choose LED mode based on whether BPM is available
        if bpm and bpm > 0:
            # Use pattern mode with multiple colors synchronized to BPM
            try:
                colors = get_multiple_album_colors(image_path, count=3)
                print(f"Extracted {len(colors)} colors for LED pattern")
                update_busytag_config_with_pattern(volume_path, image_filename, colors, bpm)
            except Exception as e:
                print(f"Warning: Could not create LED pattern: {e}")
                # Fallback to solid color
                try:
                    led_color = get_album_led_color(image_path, mode='vibrant')
                    update_busytag_config(volume_path, image_filename, led_color=led_color)
                except Exception as e2:
                    print(f"Warning: LED update failed: {e2}")
        else:
            # Use solid color mode (legacy behavior)
            try:
                led_color = get_album_led_color(image_path, mode='vibrant')
                print(f"Extracted LED color from album art: #{led_color}")
                update_busytag_config(volume_path, image_filename, led_color=led_color)
            except Exception as e:
                print(f"Warning: Could not extract LED color: {e}")

        # Trigger display refresh by remounting the volume
        volume_name = os.path.basename(volume_path)
        refresh_busytag(volume_name=volume_name)
    except Exception as e:
        print(f"Error saving image to {output_path}: {e}")