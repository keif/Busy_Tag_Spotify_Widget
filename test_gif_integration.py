#!/usr/bin/env python3
"""
Test script to verify GIF integration components work correctly
without requiring full Spotify OAuth or BusyTag device.
"""

import sys
import os

print("=" * 60)
print("Testing GIF Integration Components")
print("=" * 60)

# Test 1: Import all new modules
print("\n[1/6] Testing imports...")
try:
    from save_canvas import save_canvas, process_canvas
    from setup_gifsicle import setup_gifsicle, run_gifsicle
    from serial_operations import find_busy_tag_device, open_serial_connection
    from image_operations import convert_mp4_to_gif, create_background_with_text, overlay_gif_on_background
    from utils import delete_file, transfer_file
    print("✓ All imports successful")
except ImportError as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Gifsicle setup
print("\n[2/6] Testing gifsicle setup...")
try:
    gifsicle_path = setup_gifsicle()
    if gifsicle_path:
        print(f"✓ Gifsicle found at: {gifsicle_path}")
    else:
        print("✗ Gifsicle not found")
        sys.exit(1)
except Exception as e:
    print(f"✗ Gifsicle setup failed: {e}")
    sys.exit(1)

# Test 3: Gifsicle execution
print("\n[3/6] Testing gifsicle execution...")
try:
    output = run_gifsicle(['--version'])
    if output:
        version_line = output.split('\n')[0]
        print(f"✓ Gifsicle version: {version_line}")
    else:
        print("✗ Gifsicle execution failed")
except Exception as e:
    print(f"✗ Gifsicle test failed: {e}")

# Test 4: Check for required dependencies
print("\n[4/6] Testing Python dependencies...")
dependencies = {
    'imageio': 'imageio',
    'numpy': 'numpy',
    'PIL': 'Pillow',
    'serial': 'pyserial',
    'google.protobuf': 'protobuf'
}

all_deps_ok = True
for module_name, package_name in dependencies.items():
    try:
        __import__(module_name)
        print(f"✓ {package_name} installed")
    except ImportError:
        print(f"✗ {package_name} missing")
        all_deps_ok = False

if not all_deps_ok:
    print("\nSome dependencies are missing. Install with:")
    print("pip install imageio numpy pillow pyserial protobuf pygifsicle")

# Test 5: Check for sample GIF
print("\n[5/6] Checking for sample files...")
if os.path.exists('current_track_gif_sample.gif'):
    print("✓ Sample GIF found")
else:
    print("⚠ Sample GIF not found (not critical)")

if os.path.exists('spotify_logo.png'):
    print("✓ Spotify logo found")
else:
    print("⚠ Spotify logo not found (required for GIF overlay)")

# Test 6: Test serial device detection (non-intrusive)
print("\n[6/6] Testing BusyTag device detection...")
try:
    device_port = find_busy_tag_device()
    if device_port:
        print(f"✓ BusyTag device found at: {device_port}")
    else:
        print("⚠ No BusyTag device detected (connect device to test)")
except Exception as e:
    print(f"⚠ Device detection test skipped: {e}")

print("\n" + "=" * 60)
print("Component Test Complete!")
print("=" * 60)
print("\nNext steps:")
print("1. Connect your BusyTag device")
print("2. Play a song on Spotify")
print("3. Run: python3 main.py")
print("\nThe app will:")
print("  - Display static image with LED colors")
print("  - Download canvas video if available")
print("  - Convert to GIF and display on BusyTag")
