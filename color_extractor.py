#!/usr/bin/env python3
"""
Color Extraction Module

Analyzes album artwork to extract dominant and complementary colors
for BusyTag LED configuration.
"""

from PIL import Image
import colorsys
from collections import Counter
from typing import Tuple, List


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """
    Convert RGB tuple to hex string format for BusyTag.

    Args:
        rgb: Tuple of (r, g, b) values 0-255

    Returns:
        Hex string like "FF0000" (no # prefix)
    """
    return '{:02X}{:02X}{:02X}'.format(rgb[0], rgb[1], rgb[2])


def get_complementary_color(rgb: Tuple[int, int, int]) -> Tuple[int, int, int]:
    """
    Calculate the complementary color for a given RGB value.

    Args:
        rgb: Tuple of (r, g, b) values 0-255

    Returns:
        Complementary RGB tuple
    """
    # Convert RGB to HSV
    r, g, b = [x / 255.0 for x in rgb]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)

    # Shift hue by 180 degrees for complementary color
    h_complement = (h + 0.5) % 1.0

    # Convert back to RGB
    r_comp, g_comp, b_comp = colorsys.hsv_to_rgb(h_complement, s, v)

    return (
        int(r_comp * 255),
        int(g_comp * 255),
        int(b_comp * 255)
    )


def get_analogous_colors(rgb: Tuple[int, int, int], offset: float = 0.083) -> List[Tuple[int, int, int]]:
    """
    Get analogous colors (±30 degrees on color wheel).

    Args:
        rgb: Tuple of (r, g, b) values 0-255
        offset: Hue offset (default 0.083 = 30 degrees)

    Returns:
        List of two analogous RGB tuples
    """
    r, g, b = [x / 255.0 for x in rgb]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)

    colors = []
    for shift in [-offset, offset]:
        h_new = (h + shift) % 1.0
        r_new, g_new, b_new = colorsys.hsv_to_rgb(h_new, s, v)
        colors.append((
            int(r_new * 255),
            int(g_new * 255),
            int(b_new * 255)
        ))

    return colors


def get_dominant_color(image_path: str, num_colors: int = 5, skip_edge_pixels: int = 5) -> Tuple[int, int, int]:
    """
    Extract the dominant color from an image.

    Args:
        image_path: Path to the image file
        num_colors: Number of top colors to consider
        skip_edge_pixels: Skip edge pixels to avoid borders

    Returns:
        RGB tuple of the dominant color
    """
    # Open and resize image for faster processing
    img = Image.open(image_path)
    img = img.convert('RGB')

    # Resize to reduce processing time
    img = img.resize((150, 150), Image.Resampling.LANCZOS)

    # Crop to skip edge pixels (avoid borders/backgrounds)
    if skip_edge_pixels > 0:
        width, height = img.size
        img = img.crop((
            skip_edge_pixels,
            skip_edge_pixels,
            width - skip_edge_pixels,
            height - skip_edge_pixels
        ))

    # Get all pixels
    pixels = list(img.getdata())

    # Filter out very dark and very bright pixels (likely background)
    filtered_pixels = [
        pixel for pixel in pixels
        if 20 < sum(pixel) / 3 < 235  # Avoid pure black/white
    ]

    if not filtered_pixels:
        filtered_pixels = pixels  # Fallback if all pixels filtered

    # Count color frequency
    pixel_counts = Counter(filtered_pixels)

    # Get most common colors
    most_common = pixel_counts.most_common(num_colors)

    # Return the most common color
    return most_common[0][0]


def get_vibrant_color(image_path: str) -> Tuple[int, int, int]:
    """
    Extract a vibrant (saturated) color from the image.

    Args:
        image_path: Path to the image file

    Returns:
        RGB tuple of a vibrant color
    """
    img = Image.open(image_path)
    img = img.convert('RGB')
    img = img.resize((150, 150), Image.Resampling.LANCZOS)

    pixels = list(img.getdata())

    # Filter for vibrant colors (high saturation, moderate value)
    vibrant_pixels = []
    for pixel in pixels:
        r, g, b = [x / 255.0 for x in pixel]
        h, s, v = colorsys.rgb_to_hsv(r, g, b)

        # High saturation (> 0.5) and moderate-to-high value (> 0.3)
        if s > 0.5 and v > 0.3:
            vibrant_pixels.append(pixel)

    if not vibrant_pixels:
        # Fallback to dominant color if no vibrant colors found
        return get_dominant_color(image_path)

    # Count frequency and return most common vibrant color
    pixel_counts = Counter(vibrant_pixels)
    return pixel_counts.most_common(1)[0][0]


def adjust_brightness(rgb: Tuple[int, int, int], factor: float) -> Tuple[int, int, int]:
    """
    Adjust the brightness of an RGB color.

    Args:
        rgb: Tuple of (r, g, b) values 0-255
        factor: Brightness multiplier (0.5 = darker, 1.5 = brighter)

    Returns:
        Adjusted RGB tuple
    """
    r, g, b = [x / 255.0 for x in rgb]
    h, s, v = colorsys.rgb_to_hsv(r, g, b)

    # Adjust value (brightness)
    v = min(1.0, v * factor)

    r_new, g_new, b_new = colorsys.hsv_to_rgb(h, s, v)

    return (
        int(r_new * 255),
        int(g_new * 255),
        int(b_new * 255)
    )


def get_album_led_color(image_path: str, mode: str = 'vibrant') -> str:
    """
    Extract an appropriate LED color from album artwork.

    Args:
        image_path: Path to the album artwork image
        mode: Color extraction mode:
            - 'vibrant': Most saturated color (default)
            - 'dominant': Most common color
            - 'complementary': Complementary to dominant color
            - 'bright': Brightened dominant color

    Returns:
        Hex color string for BusyTag LED (e.g., "FF0000")
    """
    if mode == 'vibrant':
        rgb = get_vibrant_color(image_path)
    elif mode == 'dominant':
        rgb = get_dominant_color(image_path)
    elif mode == 'complementary':
        dominant = get_dominant_color(image_path)
        rgb = get_complementary_color(dominant)
    elif mode == 'bright':
        dominant = get_dominant_color(image_path)
        rgb = adjust_brightness(dominant, 1.5)
    else:
        # Default to vibrant
        rgb = get_vibrant_color(image_path)

    return rgb_to_hex(rgb)


def get_multiple_album_colors(image_path: str, count: int = 3) -> List[str]:
    """
    Extract multiple colors from album artwork for LED patterns.

    Args:
        image_path: Path to the album artwork image
        count: Number of colors to extract (2-4 recommended)

    Returns:
        List of hex color strings for BusyTag LED pattern
    """
    colors = []

    # Get vibrant color as the primary
    vibrant_rgb = get_vibrant_color(image_path)
    colors.append(rgb_to_hex(vibrant_rgb))

    if count >= 2:
        # Get dominant color
        dominant_rgb = get_dominant_color(image_path)
        # Only add if sufficiently different from vibrant
        if color_distance(vibrant_rgb, dominant_rgb) > 50:
            colors.append(rgb_to_hex(dominant_rgb))
        else:
            # Use complementary to vibrant instead
            comp_rgb = get_complementary_color(vibrant_rgb)
            colors.append(rgb_to_hex(comp_rgb))

    if count >= 3:
        # Add a brightened version of the dominant
        bright_rgb = adjust_brightness(dominant_rgb, 1.3)
        colors.append(rgb_to_hex(bright_rgb))

    if count >= 4:
        # Add complementary to dominant
        comp_dominant = get_complementary_color(dominant_rgb)
        colors.append(rgb_to_hex(comp_dominant))

    return colors[:count]


def color_distance(rgb1: Tuple[int, int, int], rgb2: Tuple[int, int, int]) -> float:
    """
    Calculate perceptual distance between two RGB colors.

    Args:
        rgb1: First RGB tuple
        rgb2: Second RGB tuple

    Returns:
        Distance value (0-441, higher = more different)
    """
    return ((rgb1[0] - rgb2[0]) ** 2 +
            (rgb1[1] - rgb2[1]) ** 2 +
            (rgb1[2] - rgb2[2]) ** 2) ** 0.5


# Testing and examples
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python color_extractor.py <image_path> [mode]")
        print("Modes: vibrant (default), dominant, complementary, bright")
        sys.exit(1)

    image_path = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else 'vibrant'

    print(f"\nAnalyzing: {image_path}")
    print(f"Mode: {mode}\n")

    try:
        # Extract color
        hex_color = get_album_led_color(image_path, mode=mode)
        print(f"LED Color (hex): {hex_color}")

        # Show additional info
        if mode == 'vibrant':
            rgb = get_vibrant_color(image_path)
        else:
            rgb = get_dominant_color(image_path)

        print(f"RGB: {rgb}")

        # Show complementary
        comp_rgb = get_complementary_color(rgb)
        comp_hex = rgb_to_hex(comp_rgb)
        print(f"Complementary Color: {comp_hex} (RGB: {comp_rgb})")

        print(f"\nBusyTag config.json LED setting:")
        print(f'{{"led_bits": 127, "color": "{hex_color}"}}')

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
