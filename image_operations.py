import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

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

def create_image_with_text(track_info, image_path, drive_letter):
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

    output_path = f"{drive_letter}//current_track_image.png"
    canvas.save(output_path)