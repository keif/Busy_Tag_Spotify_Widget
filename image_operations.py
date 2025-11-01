import os
import json
import requests
import imageio
import pygifsicle
import time
import numpy as np
import subprocess
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageSequence
from busytag_refresh import refresh_busytag
from color_extractor import get_album_led_color
from utils import delete_file
from serial_operations import open_serial_connection, find_busy_tag_device, close_serial_connection, send_serial_command

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

def handle_image_text(track_info, draw, album_image_height, font_path):
    """
    Helper function to handle text rendering for track and artist names.
    Refactored from create_image_with_text to be reusable.
    """
    track_name = track_info.get('item', {}).get('name', None)
    if track_name is None:
        print("Track name not found in track_info.")
        return None

    artist_name = track_info.get('item', {}).get('album', {}).get('artists', [{}])[0].get('name', "Unknown Artist")

    if "(feat." in track_name:
        track_name = track_name.split("(feat.")[0].strip()

    if len(track_name) < 13:
        track_font_size = 24
        artist_font_size = 18
    elif 13 <= len(track_name) <= 16:
        track_font_size = 20
        artist_font_size = 14
    elif 16 < len(track_name) <= 20:
        track_font_size = 16
        artist_font_size = 12
    else:
        track_font_size = 16
        artist_font_size = 10

    track_font = ImageFont.truetype(font_path, track_font_size)
    artist_font = ImageFont.truetype(font_path, artist_font_size)

    text_y_track = album_image_height + 2
    text_y_artist = text_y_track + track_font_size + 2

    if len(track_name) > 20:
        split_index = track_name.rfind(' ', 0, 21)
        if split_index == -1:
            split_index = 20

        first_line = track_name[:split_index]
        second_line = track_name[split_index:].strip()

        draw.text((50, text_y_track), first_line, font=track_font, fill=(255, 255, 255))
        text_y_second_line = text_y_track + track_font_size + 5
        draw.text((50, text_y_second_line), second_line, font=track_font, fill=(255, 255, 255))
        text_y_artist = text_y_second_line + track_font_size + 5
    else:
        draw.text((50, text_y_track), track_name, font=track_font, fill=(255, 255, 255))

    draw.text((50, text_y_artist), artist_name, font=artist_font, fill=(128, 128, 128))

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

    # Use the refactored text handling function
    handle_image_text(track_info, draw, album_image_height, font_path)

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

def create_background_with_text(track_info, volume_path):
    """
    Create a background canvas with text and Spotify logo for GIF overlay.
    This is used when creating animated GIFs with track info.
    """
    logo_path = "spotify_logo.png"
    canvas_width = 240
    canvas_height = 280
    album_image_height = 225

    canvas = Image.new('RGBA', (canvas_width, canvas_height), (0, 0, 0, 255))

    draw = ImageDraw.Draw(canvas)
    font_path = "MontserratBlack-3zOvZ.ttf"

    handle_image_text(track_info, draw, album_image_height, font_path)

    try:
        spotify_logo = Image.open(logo_path).convert("RGBA")
        spotify_logo = spotify_logo.resize((30, 30))
        logo_x = 13
        logo_y = canvas_height - 49
        canvas.paste(spotify_logo, (logo_x, logo_y), spotify_logo)
    except IOError:
        print("Error opening the Spotify logo image.")

    return canvas

def overlay_gif_on_background(gifsicle_path, input_gif, output_gif, background_canvas):
    """
    Overlay GIF frames onto a background canvas with track info.
    This creates the final animated GIF with album video and track details.
    """
    with Image.open(input_gif) as img:
        new_gif_frames = []
        album_image_height = 225
        album_image_width = 240

        for frame in ImageSequence.Iterator(img):
            frame_image = frame.convert("RGB")
            frame_image = frame_image.resize((album_image_width, album_image_height))

            new_frame = background_canvas.copy()
            new_frame.paste(frame_image, (0, 0))

            quantized_frame = new_frame.convert("P", palette=Image.ADAPTIVE, colors=256)
            new_gif_frames.append(quantized_frame)

        temp_gif_path = "temp_overlay.gif"
        new_gif_frames[0].save(
            temp_gif_path,
            save_all=True,
            append_images=new_gif_frames[1:],
            duration=img.info['duration'],
            loop=0,
            optimize=True
        )

    command = [
        gifsicle_path,
        '--dither',
        '--lossy=80',
        '--optimize=3',
        '--output', output_gif,
        temp_gif_path
    ]

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running gifsicle: {e}")
    finally:
        if os.path.exists(temp_gif_path):
            os.remove(temp_gif_path)

def convert_mp4_to_gif(mp4_file_path, gif_file_path, start_time=None, end_time=10, target_fps=10, resize=None, colors=256):
    """
    Convert MP4 video to GIF with customizable parameters.
    Used to convert Spotify canvas videos to animated GIFs.
    """
    try:
        if not os.path.exists(mp4_file_path):
            print(f"Error: MP4 file not found at {mp4_file_path}")
            return

        reader = imageio.get_reader(mp4_file_path)
        original_fps = reader.get_meta_data()['fps']
        frame_step = max(1, int(original_fps / target_fps))
        frames = []

        for i, frame in enumerate(reader):
            timestamp = i / original_fps
            if (start_time is None or timestamp >= start_time) and (end_time is None or timestamp <= end_time):
                if i % frame_step == 0:
                    if resize:
                        pil_image = Image.fromarray(frame)
                        pil_image = pil_image.resize(resize, Image.LANCZOS)
                        frame = np.array(pil_image)

                    frames.append(frame)

        imageio.mimsave(gif_file_path, frames, fps=target_fps, palettesize=colors, loop=0)

    except Exception as e:
        print(f"An error occurred: {e}")

def process_track_image(track_info, volume_path):
    """
    Process and display static track image with LED color extraction.
    This function combines image fetching, LED color extraction, and BusyTag updates.
    """
    new_track_name = track_info['item']['name']
    artist_name = track_info['item']['artists'][0]['name']
    track_image = get_track_image(track_info)

    # Try to use serial operations if available
    ser = open_serial_connection(find_busy_tag_device())
    if ser:
        try:
            send_serial_command(ser, "AT+SP=current_track_image.png")
            time.sleep(0.5)
            # Clean up any existing GIF
            gif_path = os.path.join(volume_path, "current_track_gif.gif")
            delete_file(gif_path)
        except Exception as e:
            print(f"Error sending serial command: {e}")
        finally:
            close_serial_connection(ser)

    if track_image:
        save_image(track_image, "track_image.png")
        create_image_with_text(track_info, "track_image.png", volume_path)
        time.sleep(3.5)

        # Try serial command again to refresh display
        if ser:
            ser = open_serial_connection(find_busy_tag_device())
            if ser:
                try:
                    send_serial_command(ser, "AT+SP=current_track_image.png")
                    time.sleep(0.5)
                except Exception as e:
                    print(f"Error sending track image to device: {e}")
                finally:
                    close_serial_connection(ser)