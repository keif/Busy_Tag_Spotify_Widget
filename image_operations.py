import os
import json
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from busytag_refresh import refresh_busytag
from color_extractor import get_album_led_color

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
        with open(config_path, 'r') as f:
            content = f.read()

        # Try to parse JSON
        try:
            config = json.loads(content)
        except json.JSONDecodeError as je:
            print(f"Warning: config.json is malformed. Creating new config.")
            print(f"JSON Error: {je}")
            # Create a minimal valid config
            config = {
                "version": 3,
                "image": image_filename,
                "show_after_drop": True,
                "allow_usb_msc": True,
                "allow_file_server": False,
                "disp_brightness": 100
            }

        # Update the image field
        config['image'] = image_filename

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

        # Write back the config
        with open(config_path, 'w') as f:
            json.dump(config, f)

        print(f"BusyTag config updated to display: {image_filename}")
        return True
    except Exception as e:
        print(f"Error updating BusyTag config: {e}")
        return False

def create_image_with_text(track_info, image_path, volume_path):
    canvas_width = 240
    canvas_height = 280

    canvas = Image.new('RGB', (canvas_width, canvas_height), (0, 0, 0))

    try:
        track_image = Image.open(image_path)
    except IOError:
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
    except IOError:
        print("Error opening the Spotify logo image.")

    image_filename = "current_track_image.png"
    output_path = os.path.join(volume_path, image_filename)

    try:
        canvas.save(output_path)
        print(f"Image saved successfully to: {output_path}")

        # Extract LED color from the album artwork
        try:
            led_color = get_album_led_color(image_path, mode='vibrant')
            print(f"Extracted LED color from album art: #{led_color}")
        except Exception as e:
            print(f"Warning: Could not extract LED color: {e}")
            led_color = None

        # Update BusyTag config to display the new image with LED color
        update_busytag_config(volume_path, image_filename, led_color=led_color)

        # Trigger display refresh by remounting the volume
        volume_name = os.path.basename(volume_path)
        refresh_busytag(volume_name=volume_name)
    except Exception as e:
        print(f"Error saving image to {output_path}: {e}")