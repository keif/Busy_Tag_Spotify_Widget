"""
Unit tests for color_extractor.

The pure color-math functions are tested directly; the image-analysis
functions are exercised against small solid-color PNGs generated on the fly
so the tests stay hermetic (no network, no device, no fixture binaries).
"""

import re

import pytest
from PIL import Image

from color_extractor import (
    adjust_brightness,
    color_distance,
    get_album_led_color,
    get_analogous_colors,
    get_complementary_color,
    get_dominant_color,
    get_multiple_album_colors,
    get_vibrant_color,
    rgb_to_hex,
)

HEX6 = re.compile(r"^[0-9A-F]{6}$")


def make_image(path, color, size=(160, 160)):
    """Write a solid-color RGB PNG to `path` and return the path as a str."""
    Image.new("RGB", size, color).save(path)
    return str(path)


# --------------------------------------------------------------------------- #
# rgb_to_hex
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize(
    "rgb, expected",
    [
        ((0, 0, 0), "000000"),        # lower boundary
        ((255, 255, 255), "FFFFFF"),  # upper boundary
        ((255, 0, 0), "FF0000"),
        ((1, 2, 3), "010203"),        # zero-padding + uppercasing
    ],
)
def test_rgb_to_hex(rgb, expected):
    assert rgb_to_hex(rgb) == expected


# --------------------------------------------------------------------------- #
# color_distance
# --------------------------------------------------------------------------- #
def test_color_distance_identical_is_zero():
    assert color_distance((10, 20, 30), (10, 20, 30)) == 0.0


def test_color_distance_black_to_white_is_max():
    # sqrt(3 * 255**2) ~= 441.67 — the documented upper bound.
    assert color_distance((0, 0, 0), (255, 255, 255)) == pytest.approx(441.67, abs=0.01)


def test_color_distance_is_symmetric():
    a, b = (200, 100, 50), (10, 90, 240)
    assert color_distance(a, b) == color_distance(b, a)


# --------------------------------------------------------------------------- #
# get_complementary_color
# --------------------------------------------------------------------------- #
def test_complementary_of_red_is_cyan():
    assert get_complementary_color((255, 0, 0)) == (0, 255, 255)


def test_complementary_is_involutive_within_rounding():
    # Applying the 180-degree hue shift twice returns to the original hue;
    # only integer-rounding drift should remain.
    original = (200, 120, 40)
    round_trip = get_complementary_color(get_complementary_color(original))
    for got, want in zip(round_trip, original, strict=True):
        assert abs(got - want) <= 3


# --------------------------------------------------------------------------- #
# get_analogous_colors
# --------------------------------------------------------------------------- #
def test_analogous_returns_two_valid_colors():
    colors = get_analogous_colors((200, 50, 50))
    assert len(colors) == 2
    for c in colors:
        assert len(c) == 3
        assert all(0 <= channel <= 255 for channel in c)


# --------------------------------------------------------------------------- #
# adjust_brightness
# --------------------------------------------------------------------------- #
def test_adjust_brightness_identity_factor_preserves_color():
    original = (120, 60, 30)
    result = adjust_brightness(original, 1.0)
    for got, want in zip(result, original, strict=True):
        assert abs(got - want) <= 2


def test_adjust_brightness_clamps_value_at_one():
    # A large factor must not push any channel past 255 (value clamps to 1.0).
    result = adjust_brightness((200, 100, 50), 5.0)
    assert all(0 <= channel <= 255 for channel in result)
    assert max(result) == 255


def test_adjust_brightness_zero_factor_is_black():
    assert adjust_brightness((200, 100, 50), 0.0) == (0, 0, 0)


# --------------------------------------------------------------------------- #
# get_dominant_color (image-based)
# --------------------------------------------------------------------------- #
def test_dominant_color_of_solid_image(tmp_path):
    path = make_image(tmp_path / "solid.png", (200, 50, 50))
    assert get_dominant_color(path) == (200, 50, 50)


def test_dominant_color_falls_back_when_all_pixels_filtered(tmp_path):
    # Pure black is filtered out by the brightness gate; the function should
    # fall back to the unfiltered pixels rather than crash on an empty set.
    path = make_image(tmp_path / "black.png", (0, 0, 0))
    assert get_dominant_color(path) == (0, 0, 0)


# --------------------------------------------------------------------------- #
# get_vibrant_color (image-based)
# --------------------------------------------------------------------------- #
def test_vibrant_color_picks_saturated_color(tmp_path):
    path = make_image(tmp_path / "red.png", (255, 0, 0))
    assert get_vibrant_color(path) == (255, 0, 0)


def test_vibrant_color_falls_back_to_dominant_on_gray(tmp_path):
    # A desaturated image has no "vibrant" pixels, so it must fall back to
    # the dominant color instead of returning nothing.
    path = make_image(tmp_path / "gray.png", (128, 128, 128))
    assert get_vibrant_color(path) == (128, 128, 128)


# --------------------------------------------------------------------------- #
# get_album_led_color (mode dispatch)
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("mode", ["vibrant", "dominant", "complementary", "bright"])
def test_album_led_color_returns_valid_hex_for_each_mode(tmp_path, mode):
    path = make_image(tmp_path / "art.png", (180, 60, 90))
    assert HEX6.match(get_album_led_color(path, mode=mode))


def test_album_led_color_unknown_mode_falls_back_to_vibrant(tmp_path):
    path = make_image(tmp_path / "art.png", (255, 0, 0))
    assert get_album_led_color(path, mode="does-not-exist") == "FF0000"


# --------------------------------------------------------------------------- #
# get_multiple_album_colors
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("count", [1, 2, 3, 4])
def test_multiple_album_colors_returns_requested_count(tmp_path, count):
    path = make_image(tmp_path / "art.png", (200, 120, 40))
    colors = get_multiple_album_colors(path, count=count)
    assert len(colors) == count
    for c in colors:
        assert HEX6.match(c)
